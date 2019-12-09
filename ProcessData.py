from classes.ArduinoCommunicator import *
from classes.CTDatabase import *
from utils.plotting import *
import MySQLdb
import sys
import random


if __name__ == '__main__':
    data = []
    timestamps = []
    sessions = []

    Arduino = ArduinoCommunicator('/dev/cu.usbserial-1420')
    DB = CTDatabase(user="device", passwd="device")


    db = MySQLdb._mysql.connect(host="localhost",
                                user="device",
                                passwd="device",
                                db="chargingtracker")

    db.query("SELECT ses from data "
             "order by ts desc "
             "limit 1")

    dbres = db.store_result()
    result = dbres.fetch_row()[0][0]
    session = int(result) + 1

    print('STATUS : Running session ' + str(session))
    tag = input('Please type tag of session:\n')

    print(tag)

    db_data = '(' + str(session) + ', \"' + tag + '\" )'
    db.query("""insert into metatags (session, tag) values """ + db_data)


    reference_time = time.time()
    while 1:
        try:
            # measure = Arduino.RequestData('A0? -mean 10\n')
            # measure = Arduino.Request_V1_AD(10)
            # voltage = measure[0]
            # current = measure[1]
            current = random.randint(1,10) * -0.1
            voltage = random.randint(1,10) * -0.1
            time.sleep(0.1)
            data.append(current)
            ts = time.time() - reference_time
            timestamps.append(ts)
            sessions.append(session)
            print("ts= {:2f} V1={:2f} A={:2f} Session={:} ".format(ts, voltage, current, session))
            # print(str(ts) + "  " + str(current) + "  " + str(session))

            db_data = '(' + str(ts) + ', ' + str(current) + ', ' + str(voltage) + ', ' + str(session) + ')'
            db.query("""insert into data (pyts, A, V1, ses) values """ + db_data)
        except KeyboardInterrupt:
            print('\nSTATUS : Exit session...')
            sys.exit()






