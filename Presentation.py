from utils.plotting import *
from matplotlib import pyplot as plt
from classes.CTDatabase import *

#TODO:
'''
function that presents graph of one whole cycle specified by number
function that shows the different cycles to choose from
function that shows ongoing cycle
calculate total power and show in graph

'''


def plot_sessions(sessions, DB:CTDatabase, title='Tracked charging cycles'):

    plt.figure(figsize=(12,8))

    col = ['b', 'r', 'g', 'o']

    filename = 'complete_charging_cycles'

    for i, session in enumerate(sessions):
        filename += '-' + str(session)
        data = DB.get_session_data(session)
        energy = DB.get_session_energy(session)
        tag = DB.get_session_tag(session)

        plt.plot(np.array(np.array(data[1])), np.array(data[2]) * np.array(data[2]), linestyle='-', marker='.',
                 color=col[i], label='\n'.join([r"session: " + str(session),
                                                r"description: " + tag,
                                                r"$E = {:.2f} Wh$".format(energy)]))
    # Plot properties
    plt.grid(False)
    plt.legend(loc='best')
    plt.title(title)
    plt.xlabel(r'Time in $ s $')
    plt.ylabel(r'Power in $ W $')

    plt.savefig('graphics/' + filename + '.png', dpi=300)


def live_plot(DB:CTDatabase):
    session = DB.get_latest_session()

    while 1:
        data = DB.fetch_new_data(session)
        if data is None:
            break

        print(data)
        # TODO: Continously update figure with new data



if __name__ == '__main__':
    DB = CTDatabase()

    #session = 4
    #data = DB.get_session_data(session)
    #plot2D_x_y(data[1], data[2], 'session '+str(session), xlabel='seconds', ylabel='current in A', title='Charging cycle session '+str(session))

    sessions = [11,12]
    plot_sessions(sessions, DB)



