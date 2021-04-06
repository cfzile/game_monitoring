import datetime
import psycopg2
import pytz
from telethon import TelegramClient, utils
from telethon.tl.types import PeerUser, PeerChat, PeerChannel, UserStatusOffline, UserStatusOnline
import asyncio
from time import gmtime, strftime
import time


def get_status(USER_ID):
    api_id = 1964246
    api_hash = '304623578146026d5a64187b41f81433'
    client = TelegramClient('session_name', api_id, api_hash)
    client.start()
    loop = asyncio.get_event_loop()
    user = loop.run_until_complete(client.get_entity(USER_ID))
    return isinstance(user.status, UserStatusOnline)


connection = psycopg2.connect(user="k118vjfsmunlf2wya38n3j3qykk",
                              password="11auomgwub9rjl81w7gybevb76hbvz5zy8tk52loj1mfe9023s",
                              host="localhost",
                              port="5432",
                              database="collect_data")
cursor = connection.cursor()

cursor.execute("select * from hundle_user where server='telegram'")

records = cursor.fetchall()
ids = []
for record in records:
    ids.append([record[0], record[2]])

cursor.close()
connection.close()

while True:
    print("OK")
    for ID, USER_ID in ids:
        connection = psycopg2.connect(user="k118vjfsmunlf2wya38n3j3qykk",
                                      password="11auomgwub9rjl81w7gybevb76hbvz5zy8tk52loj1mfe9023s",
                                      host="localhost",
                                      port="5432",
                                      database="collect_data")
        cursor = connection.cursor()

        try:
            user_status = int(get_status(USER_ID))
            T = datetime.datetime.now().astimezone(pytz.timezone("Europe/Moscow"))
            date = "%d.%d.%d" % (T.day, T.month, T.year)
            t = T.hour * 60 + T.minute
            cursor.execute("set timezone = 'Europe/Moscow'")
            cursor.execute("insert into hundle_data (user_id, date, time, status)"
                           " values (" + str(ID) + ",  (current_date at time zone 'Europe/Moscow')::date ," + str(t) + "," + str(user_status) + ")")
        except:
            print("Error")
        connection.commit()
        cursor.close()
        connection.close()
    time.sleep(5000)
