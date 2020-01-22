from classes.CTDatabase import *

if __name__ == "__main__":

    DB = CTDatabase()

    session = DB.get_latest_session()
    print('STATUS : Running session ' + str(session))

    reference_time = time.time()
    while 1:
        try:
            battery = int(input("Please input percentage: "))

            pyts = time.time() - reference_time
            DB.add_percentage_keypoint(pyts, session, battery)
            print("pyts={:2f} battery={}% data "
                  "written to db".format(pyts, battery))

        except KeyboardInterrupt:
            print('\nSTATUS : Exit session...')
            break

        except ValueError:
            print('ERROR : Please only use integers.')
            continue


