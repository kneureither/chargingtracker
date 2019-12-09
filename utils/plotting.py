#!/usr/local/bin/python
#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

cus_linestyle = None

def plot2D_x_y(xdata, ydata, name='data', title='figure1', xlabel='x axis', ylabel='y_axis'):
    if xdata is None or ydata is None:
        print('Invalid data!')

    plt.plot(np.array(xdata), np.array(ydata), linestyle=cus_linestyle, marker='o', label=name, color='b')

    # Plot properties
    plt.grid(True)
    plt.legend(loc='best')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.savefig('graphics/' + title + '.png', dpi=300)
