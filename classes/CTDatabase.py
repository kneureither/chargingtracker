import MySQLdb
import heapq
import time
import numpy as np

class CTDatabase:
    """
    Interface for working with chargingtracker database.
    """

    def __init__(self, host="localhost", user="presentation",
                 passwd="presentation", db="chargingtracker"):
        """
        initializes connection to database.

        :param host: database host
        :param user: mysql user
        :param passwd: user password
        :param db: database
        """
        self.db = MySQLdb._mysql.connect(host=host,
                                         user=user,
                                         passwd=passwd,
                                         db=db)

        #varibles for live plotting
        self.buffer = []
        self.ts_reference = 0.0

    def get_session_data(self, session):
        """
        Reads complete session from database.

        :param session: int
        :return: data session data as 4 dim array with (ts, pyts, A0, session) arrays
        """

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
        """
        Reads tag for session, stored in separate database table 'metatags'.

        :param session: str
        :return: str of session tag
        """
        self.db.query("SELECT * from metatags where session=" + str(session))
        dbres = self.db.store_result()
        result = dbres.fetch_row(maxrows=1)[0]

        return result[2].decode("utf-8")

    def get_session_battery_data(self, session):
        """
        Reads battery data for session, stored in separate database table 'devicebattery'.

        :param session: int
        :return: array containing the battery data, format of one entry: (ts, pyts, session, batteryvalue)
        """
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
        """
        Get the session value of the most recent data in the database.
        :return: int
        """
        self.db.query("SELECT ses from data "
                 "order by ts desc "
                 "limit 1")

        dbres = self.db.store_result()
        result = dbres.fetch_row()[0][0]
        return int(result)

    def set_session_tag(self, session, tag):
        """
        Works with table 'metatags' and adds a value which assigns a str tag to a session number.
        :param session: int
        :param tag: str
        """
        db_data = '(' + str(session) + ', \"' + tag + '\" )'
        self.db.query("""insert into metatags (session, tag) values """ + db_data)

    def add_percentage_keypoint(self, pyts, session, percentage):
        """
        Adds an entry to table 'devicebattery'.
        """
        self.db.query("""insert into devicebattery (pyts, session, percentage) values
                         ({}, {}, {})""".format(pyts, session, percentage))

    def add_data(self, pyts, current, voltage, session):
        """
        Adds a value to the charging data table 'data'.
        :param pyts: float
        :param current: float
        :param voltage: float
        :param session: int
        """
        db_data = '(' + str(pyts) + ', ' + str(current) + ', ' \
                  + str(voltage) + ', ' + str(session) + ')'
        self.db.query("""insert into data (pyts, A, V1, ses) values """ + db_data)

    def _fetch_once(self, session):
        """
        Gathers all available session data from database and stores is in a buffer.
        Then iteratively returns one tuple for every call.
        When buffer is empty, it tries to fetch data again until there is no new data added anymore
        for the session.

        :param session: int
        :return: tuple of charging data if new data available, else None.
        """
        if self.buffer:
            pass
        else:
            self.db.query("SELECT pyts, A, V1, ses from data where ses=" + str(session) + " and pyts > " + str(self.ts_reference))
            dbres = self.db.store_result()
            result = dbres.fetch_row(maxrows=0)

            #print(result)

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
        """
        This function is a preparation for real time plotting.
        Gets data entries iteratively from database.

        :returns:   None if there is no data added and everything delivered,
                    next tuple (pyts, V1, A, session) if there is still data that was not read.
        """
        for i in range(2):
            data = self._fetch_once(session)
            if data == None:
                # Wait twice, if there is new data, if not, assume, that no data is added to db anymore.
                time.sleep(2)
            else:
                i=0
                return data

        # Reset reference timestamp, will only be reached, if there is no data added.
        self.ts_reference = 0.0
        return None


    def get_session_energy(self, session):
        """
        Reads the charging data of one complete session and calculates the energy in Wh.
        :param session: int
        :return: float energy (in Wh)
        """
        data = self.get_session_data(session)

        energy = 0
        for i in range(1, len(data[0])):
            power = np.array(data[2][i]) * np.array(data[3][i])
            energy += power * (data[1][i] - data[1][i-1])

        # Convert Ws to Wh
        energy = energy / 3600
        return energy

if __name__ == "__main__":
    """
    Some testing code.
    """

    CT = CTDatabase()
    CT.add_data(0.0, 1.0, 2.0, 0)
    # print(CT.get_session_energy(18))
