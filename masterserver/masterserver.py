from socket import *
import time
import io
import psycopg2
from a2s.defaults import DEFAULT_TIMEOUT, DEFAULT_ENCODING
from a2s.byteio import ByteReader, ByteWriter
import sys

import sys, os, time, atexit
from signal import SIGTERM


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
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
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
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
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

    def start(self, logger, port):
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
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run(logger, port=27011)

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
            sys.stderr.write(message % self.pidfile)
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

    def restart(self, logger, port=27011):
        """
        Restart the daemon
        """
        self.stop()
        self.start(logger, port)

    def run(self, logger, port=27011):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """


class MasterServer(Daemon):
    LIMIT = 100

    def write_records(self, records, writer, cur_num=0):
        for record in records:
            b1, b2, b3, b4 = map(int, record[1].split('.'))
            writer.write_uint8(b1)
            writer.write_uint8(b2)
            writer.write_uint8(b3)
            writer.write_uint8(b4)
            writer.write_uint16(int(record[2]))
            cur_num += 1
            if cur_num == self.LIMIT:
                break
        return cur_num

    def run(self, logger, port=27011):

        timeout = DEFAULT_TIMEOUT
        encoding = DEFAULT_ENCODING
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        udp_socket.bind(('0.0.0.0', port))

        top_servers = open(self.basedir + "/" + "top_servers.db_query").read()
        top_table_servers = open(self.basedir + "/" + "top_table_servers.db_query").read()
        outside_top = open(self.basedir + "/" + "outside_top.db_query").read()

        while True:
            data, addr = udp_socket.recvfrom(1024)
            reader = ByteReader(io.BytesIO(data), endian=">", encoding=encoding)

            # reader.read_cstring()
            # _filter_ = reader.read_cstring()
            # print(_filter_)
            # # TODO: Filter

            message = b'\xFF\xFF\xFF\xFF\x66\x0A'
            writer = ByteWriter(io.BytesIO(b''), endian=">")

            try:
                connection = psycopg2.connect(user="k118vjfsmunlf2wya38n3j3qykk",
                                              password="11auomgwub9rjl81w7gybevb76hbvz5zy8tk52loj1mfe9023s",
                                              host="localhost",
                                              port="5432",
                                              database="css-v34-monitoring")
                cursor = connection.cursor()

                logger.write(str(connection.get_dsn_parameters()) + "\n")

                cursor.execute(top_servers)
                records = cursor.fetchall()
                total = self.write_records(records, writer)
                cursor.execute(top_table_servers)
                records = cursor.fetchall()
                total += self.write_records(records, writer, total)
                cursor.execute(outside_top)
                records = cursor.fetchall()
                total += self.write_records(records, writer, total)

                logger.write("You are connected, total=%d\n" % total)

            except (Exception, psycopg2.Error) as error:
                logger.write("Error while connecting to PostgreSQL:\n")
                logger.write(error)
            finally:
                if connection:
                    cursor.close()
                    connection.close()
                    logger.write("PostgreSQL connection is closed")

            writer.write_uint8(0)
            writer.write_uint8(0)
            writer.write_uint8(0)
            writer.write_uint8(0)
            writer.write_uint16(0)
            message += writer.stream.getvalue()
            udp_socket.sendto(message, addr)

            logger.write("Send answer on %s:%d" % (addr[0], addr[1]))


def main():
    logger = open(sys.argv[1], "a")
    port = 27011
    if len(sys.argv) > 2:
        port = sys.argv[2]

    # T = time.time()
    # si = sys.argv[1] + "/" + "daemon_%s_in" % str(T)
    # so = sys.argv[1] + "/" + "daemon_%s_out" % str(T)
    # se = sys.argv[1] + "/" + "daemon_%s_err" % str(T)
    #
    # open(si, "a").close()
    # open(so, "a").close()
    # open(se, "a").close()

    MasterServer(os.path.dirname(os.path.abspath(__file__)), "pidfile").start(logger, port)


main()
