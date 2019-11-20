import serial
import time
from utils.plotting import *
import numpy as np

class ArduinoCommunicator:
    def __init__(self):
        self.ser = serial.Serial(
            port='/dev/cu.usbmodem14101',
            baudrate=9600,
            parity=serial.PARITY_ODD,
            stopbits=serial.STOPBITS_TWO,
            bytesize=serial.SEVENBITS
        )

    def Request(self, message):
        ser.



current_data = []
data_count = 100

for i in range(data_count):
    serial_string = ser.readline()
    serial_data = float(serial_string[-8:-2])
    print(serial_data)
    current_data.append(serial_data)

ser.close()

time = np.linspace(0, data_count, num=data_count, endpoint=False) * 100
print(time)
plot2D_x_y(time, current_data, name='Measured current', xlabel='time ms')



