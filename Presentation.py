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

        mean_count = 300
        mean_data = create_mean_data(mean_count, data)

        plt.plot(np.array(np.array(data[1])), np.array(data[2]) * np.array(data[2]), linestyle='-', marker='.',
                 color=col[2*i], label='\n'.join([r"session: " + str(session),
                                                r"description: " + tag,
                                                r"$E = {:.2f} Wh$".format(energy)]))
        plt.plot(np.array(np.array(mean_data[1])), np.array(mean_data[2]) * np.array(mean_data[2]), linestyle='-',
                 marker=None, color=col[2*i+1], label='\n'.join([r"session: " + str(session),
                                                              r"mean over $N={:}$ values".format(mean_count)]))

    # Plot properties
    plt.grid(False)
    plt.legend(loc='best')
    plt.title(title)
    plt.xlabel(r'Time in $ s $')
    plt.ylabel(r'Power in $ W $')

    plt.savefig('graphics/' + filename + '.png', dpi=300)


def create_mean_data(mean_count, data):
    start_index = int(mean_count / 2)
    end_index = len(data[0]) - start_index

    mean_data = [[] for i in range(5)]

    for i in range(start_index, end_index):
        mean_data[0].append(data[0][i])
        mean_data[1].append(data[1][i])
        mean_data[2].append(0.0)
        mean_data[3].append(0.0)
        mean_data[4].append(data[4][i])

        for j in range(mean_count):
            mean_data[2][i-start_index] += data[2][i-start_index + j] / float(mean_count)
            mean_data[3][i-start_index] += data[3][i-start_index + j] / float(mean_count)

    return mean_data


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

    sessions = [15]
    plot_sessions(sessions, DB)



