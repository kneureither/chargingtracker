import MySQLdb
from utils.plotting import *

#TODO:
'''
function that presents graph of one whole cycle specified by number
function that shows the different cycles to choose from
function that shows ongoing cycle
calculate total power and show in graph

'''

class CTDatabase:
    '''Interface for working with chargingtracker database'''


    def __init__(self, host="localhost", user="presentation", passwd="presentation", db="chargingtracker"):
        self.db = MySQLdb._mysql.connect(host=host,
                                    user=user,
                                    passwd=passwd,
                                    db=db)

    def get_session_data(self, session):
        '''returns session data as 4 dim array with (ts, pyts, A0, session) arrays'''

        self.db.query("SELECT * from data where ses=4")
        dbres = self.db.store_result()
        result = dbres.fetch_row(maxrows=0)

        data = [[] for i in range(4)]

        for entry in result:
            data[0].append(entry[0])
            data[1].append(float(entry[1]))
            data[2].append(float(entry[2]))
            data[3].append(int(entry[3]))

        return data

    def get_session_power(self, session):
        pass


if __name__ == '__main__':
    DB = CTDatabase()

    session = 4
    data = DB.get_session_data(session)

    plot2D_x_y(data[1], data[2], 'session '+str(session), xlabel='seconds', ylabel='current in A', title='Charging cycle session '+str(session))