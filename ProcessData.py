from classes.ArduinoCommunicator import *
from utils.plotting import *
import MySQLdb


if __name__ == '__main__':
    data = []
    timestamps = []
    sessions = []

    Arduino = ArduinoCommunicator('/dev/cu.usbserial-1420')

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
    tag = input('Please specify tag of session')

    

    reference_time = time.time()
    for i in range(1000):
        measure = Arduino.RequestData('A0? -mean 10\n')
        data.append(measure)
        ts = time.time() - reference_time
        timestamps.append(ts)
        sessions.append(session)
        print(str(ts) + "  " + str(measure) + "  " + str(session))

        db_data = '(' + str(ts) + ', ' + str(measure) + ', ' + str(session) + ')'
        db.query("""insert into data (pyts, A0, ses) values """ + db_data)



