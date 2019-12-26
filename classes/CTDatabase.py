import MySQLdb
import heapq
import time

class CTDatabase:
    '''
    Interface for working with chargingtracker database.
    '''

    def __init__(self, host="localhost", user="presentation", passwd="presentation", db="chargingtracker"):
        self.db = MySQLdb._mysql.connect(host=host,
                                    user=user,
                                    passwd=passwd,
                                    db=db)
        self.buffer = []
        self.ts_reference = 0.0

    def get_session_data(self, session):
        '''returns session data as 4 dim array with (ts, pyts, A0, session) arrays'''

        self.db.query("SELECT * from data where ses=" + str(session))
        dbres = self.db.store_result()
        result = dbres.fetch_row(maxrows=0)

        data = [[] for i in range(5)]

        for entry in result:
            data[0].append(entry[0])
            data[1].append(float(entry[1]))
            data[2].append(float(entry[2]))
            data[3].append(float(entry[3]))
            data[4].append(int(entry[4]))

        return data

    def get_session_tag(self, session):
        """reads tag for session, stored in separate database metatags"""
        self.db.query("SELECT * from metatags where session=" + str(session))
        dbres = self.db.store_result()
        result = dbres.fetch_row(maxrows=1)[0]

        return result[2].decode("utf-8")

    def get_session_battery_data(self, session):
        """reads battery data for session, stored in separate database devicebattery"""
        if session < 16:
            return None

        self.db.query("SELECT * from devicebattery where session={}".format(session))
        dbres = self.db.store_result()
        result = dbres.fetch_row(maxrows=0)

        data = [[] for i in range(4)]

        for entry in result:
            data[0].append(entry[0])
            data[1].append(float(entry[1]))
            data[2].append(int(entry[2]))
            data[3].append(int(entry[3]))

        return data

    def get_latest_session(self):
        self.db.query("SELECT ses from data "
                 "order by ts desc "
                 "limit 1")

        dbres = self.db.store_result()
        result = dbres.fetch_row()[0][0]
        return int(result)

    def set_session_tag(self, session, tag):
        db_data = '(' + str(session) + ', \"' + tag + '\" )'
        self.db.query("""insert into metatags (session, tag) values """ + db_data)

    def add_percentage_keypoint(self, pyts, session, percentage):
        self.db.query("""insert into devicebattery (pyts, session, percentage) values 
                         ({}, {}, {})""".format(pyts, session, percentage))

    def add_data(self, pyts, current, voltage, session):
        db_data = '(' + str(pyts) + ', ' + str(current) + ', ' + str(voltage) + ', ' + str(session) + ')'
        self.db.query("""insert into data (pyts, A, V1, ses) values """ + db_data)

    def _fetch_once(self, session):
        if self.buffer:
            pass
        else:
            self.db.query("SELECT pyts, A, V1, ses from data where ses=" + str(session) + " and pyts > " + str(self.ts_reference))
            dbres = self.db.store_result()
            result = dbres.fetch_row(maxrows=0)

            print(result)

            if len(result) == 0:
                return None

            for entry in result:
                pyts = float(entry[0])
                V1 = float(entry[1])
                A = float(entry[2])
                session = int(entry[3])

                print("ts= {:2f} V1={:2f} A={:2f} Session={:} ".format(pyts, A, V1, session))

                heapq.heappush(self.buffer, (pyts, V1, A, session))
                self.ts_reference = pyts

        # In order to preserve the format restore a tuple entry where the mysql timestamp should be
        entry = heapq.heappop(self.buffer)
        return (None, entry[0], entry[1], entry[2], entry[3])

    def fetch_new_data(self, session):
        '''
        gets data entries iteratively from database.

        :returns:   None if there is no data added and everything delivered,
                    next tuple (pyts, V1, A, session) if there is still data that was not read.
        '''
        for i in range(2):
            data = self._fetch_once(session)
            if data == None:
                # Wait twice, if there is new data, if not, assume, that no data is added to db anymore.
                time.sleep(1)
            else:
                i=0
                return data

        # Reset reference timestamp, will only be reached, if there is no data added.
        self.ts_reference = 0.0
        return None


    def get_session_energy(self, session):
        data = self.get_session_data(session)

        energy = 0
        for i in range(1, len(data[0])):
            #power = data[2][i] * data[3][i]
            power = data[2][i] * 5.0
            energy += power * (data[1][i] - data[1][i-1])

        # Convert Ws to Wh
        energy = energy / 3600
        return energy