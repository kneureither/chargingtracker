from utils.plotting import *
from matplotlib import pyplot as plt
from classes.CTDatabase import *


def plot_sessions(sessions, DB:CTDatabase, title='Tracked charging cycles', draw_battery=True):
    """
    Saves a plot of all sessions that are passed in the sessions array.

    :param sessions: integer array of session ids
    :param DB: database that contains the data
    :param title: title of the plot
    :param draw_battery: True of percentage tags should be plotted, False if not
    :return:
    """

    plt.figure(figsize=(12,8))

    col = ['b', 'r', 'g', 'r', 'c', 'r', 'm', 'y', 'k']

    filename = 'complete_charging_cycles'

    for i, session in enumerate(sessions):
        filename += '-' + str(session)
        
        #  get data from database
        data = DB.get_session_data(session)
        energy = DB.get_session_energy(session)
        tag = DB.get_session_tag(session)
        battery_data = DB.get_session_battery_data(session)

        mean_count = 300
        mean_data = create_mean_data(mean_count, data)

        plt.plot(np.array(np.array(data[1])), np.array(data[2]), linestyle='', marker='.',
                 color=col[2*i], label='\n'.join([r"session: " + str(session),
                                                r"tag: {}".format(tag),
                                                r"$E = {:.2f} Wh$".format(energy)]))
        plt.plot(np.array(np.array(mean_data[1])), np.array(mean_data[2]), linestyle='-',
                 marker=None, color=col[2*i+1], label='\n'.join([r"mean over $N={:}$ values".format(mean_count)]))

        if draw_battery and battery_data is not None:
            for j in range(len(battery_data[0])):
                plt.axvline(x=battery_data[1][j], color=col[2*i], ymax=1.5,
                             ymin=1.5)
                plt.annotate("{}%".format(battery_data[3][j]),
                             (battery_data[1][j], 0.3 + 0.4*i),
                             textcoords="offset points",  # how to position the text
                             xytext=(0, 0),  # distance from text to points (x,y)
                             ha='center',
                             color=col[2*i],
                             bbox=dict(facecolor='white', edgecolor=col[2*i]))

    # Plot properties
    plt.grid(False)
    plt.legend(loc='best')
    plt.title(title)
    plt.xlabel(r'Time in $ s $')
    # plt.ylabel(r'Power in $ W $')
    plt.ylabel(r'Current in $ Ampere $')

    plt.savefig('graphics/' + filename + '.png', dpi=300)


def create_mean_data(mean_count, data):
    """
    Creates a running mean of the data delivered taking into account the previous and following
    mean_count/2 values for every point in the data array.

    :param mean_count: integer
    :param data: data from database
    :return: mean data from data
    """

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
    """
    Creates a live plot by always updating it with new data.

    :param DB: database which is continuously updated.
    :return:
    """
    session = DB.get_latest_session()

    while 1:
        data = DB.fetch_new_data(session)
        if data is None:
            break

        print(data)
        # TODO: Continously update figure with new data



if __name__ == '__main__':

    DB = CTDatabase()
    # specify which sessions should be included
    sessions = [15, 16, 18]
    plot_sessions(sessions, DB)





