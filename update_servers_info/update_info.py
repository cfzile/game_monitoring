import sys, os, time, atexit
from aifc import Error
from datetime import datetime
from signal import SIGTERM
import a2s
import psycopg2

from fuzzywuzzy import process


class Daemon:

    def __init__(self, basedir, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.basedir = basedir
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):

        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as e:
            print("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            print("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        # sys.stdout.flush()
        # sys.stderr.flush()
        # si = open(self.stdin, 'r')
        # so = open(self.stdout, 'a+')
        # se = open(self.stderr, 'a+', 0)
        # os.dup2(si.fileno(), sys.stdin.fileno())
        # os.dup2(so.fileno(), sys.stdout.fileno())
        # os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        open(self.basedir + "/" + self.pidfile, 'w+').write("%s\n" % pid)

    def delpid(self):
        os.remove(self.basedir + "/" + self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = open(self.basedir + "/" + self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            print(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = open(self.basedir + "/" + self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            print(message % self.pidfile)
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err))
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """


class Updater(Daemon):

    def run(self):

        try:
            while True:

                connection = psycopg2.connect(user="k118vjfsmunlf2wya38n3j3qykk",
                                              password="11auomgwub9rjl81w7gybevb76hbvz5zy8tk52loj1mfe9023s",
                                              host="localhost",
                                              port="5432",
                                              database="css-v34-monitoring")
                connection.autocommit = True
                cursor = connection.cursor()

                cursor.execute('SELECT * FROM monitoring_server order by date_last_update')
                records = cursor.fetchall()

                for record in records:
                    ip = record[1]
                    port = record[2]

                    try:
                        print('start')
                        address = (ip, int(port))
                        info = a2s.info(address, timeout=2)

                        player_count = info.player_count
                        max_players = info.max_players
                        map_name = info.map_name
                        name = info.server_name
                        status = "connected"
                        BASE_DIR = self.basedir[:-19]
                        a = process.extract(map_name, os.listdir(BASE_DIR + "/media/monitoring/servers_avatar/"))
                        a = sorted(a, key=lambda x: x[1])
                        avatar = "monitoring/servers_avatar/no_screenshot.jpg"
                        if a[-1][1] > 70:
                            avatar = "monitoring/servers_avatar/" + a[-1][0]

                        name.replace("'", "''")
                        name.replace('"', '\"')

                        sql = """ UPDATE monitoring_server SET player_count = %s, max_players = %s, map_name = %s, name = %s, status = %s, date_last_update=now(), avatar = %s WHERE monitoring_server.id = %s  """
                        cursor.execute(sql, (player_count, max_players, map_name, name, status, avatar, record[0]))

                        # connection.commit()
                        print('end')
                        # cursor.fetchall()
                    except Exception as err:
                        print("%s %s %d" % (self.pidfile, ip, port))
                        print(err)

                cursor.close()
                time.sleep(30)
        except Exception as err:
            print('Global: ', err)


def main():
    i = int(sys.argv[1])
    time.sleep(30 * min((i - 1), 1))
    with open(os.path.dirname(os.path.abspath(__file__)) + "/pidfile_%d" % i, "a"):
        pass
    with open(os.path.dirname(os.path.abspath(__file__)) + "/pidfile_%d" % i, "w"):
        pass
    Updater(os.path.dirname(os.path.abspath(__file__)), "pidfile_%d" % i).start()


main()
