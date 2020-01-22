from classes.ArduinoCommunicator import *
from classes.CTDatabase import *
from utils.plotting import *
import MySQLdb
import sys
import random


if __name__ == '__main__':

    Arduino = ArduinoCommunicator('/dev/cu.usbserial-1410')
    DB = CTDatabase(user="device", passwd="device")


    session = DB.get_latest_session() + 1
    print('STATUS : Running session ' + str(session))
    tag = input('Please type tag of session:\n')
    print(tag)
    DB.set_session_tag(session, tag)


    reference_time = time.time()
    while 1:
        try:
            measure = Arduino.Request_V1_AD(10)
            voltage = measure[0]
            current = measure[1]
            time.sleep(0.1)
            pyts = time.time() - reference_time
            print("ts= {:2f} V1={:2f} A={:2f} "
                  "Session={:} ".format(pyts, voltage, current, session))

            DB.add_data(pyts, current, voltage, session)

        except KeyboardInterrupt:
            print('\nSTATUS : Exit session...')
            sys.exit()






