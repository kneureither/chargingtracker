import serial
import time
from utils.plotting import *
import numpy as np

class ArduinoCommunicator:
    def __init__(self):
        self.conn_closed = False
        self.ser = serial.Serial(
            port='/dev/cu.usbserial-1410',
            baudrate=9600,
            timeout=1
        )

        # parity = serial.PARITY_ODD,
        # stopbits = serial.STOPBITS_TWO,
        # bytesize = serial.SEVENBITS,

        #   self.ser.flushInput()
        time.sleep(1)


        # status = self._request('Status?')
        # self.mean_delay = status['mean delay']
        # self.stream_delay = status['stream delay']
        # self.resistance = status['resistance']


    def __del__(self):
        # if self.conn_closed:
        #     self.ser.close()
        #     self.conn_closed = True
        pass

    def __enter__(self):
        return self

    def __exit__(self):
        self.ser.close()
        self.conn_closed = True

    def _request(self, message):
        self.ser.write(message.encode())
        time.sleep(0.05)
        response = self.ser.readline().decode()
        print("response: ")
        print(response)
        if response[:5] == 'ERROR':
            raise Exception('Arduino reported Error: ' + response[8:])
        return response

    def RequestData(self, message):
        response = self._request(message)
        index_in = response.find(' ')
        if index_in == -1:
            raise IndexError('No valid data found in response from arduino. In index')
        index_out = index_in + response[index_in:].find(' ')
        if index_out == -1:
            raise IndexError('No valid data found in response from arduino. Out index')

        return float(response[index_in:index_out])

    def Receive(self):
        return self.ser.readline()

    def Tell(self, message):
        message = message + '\n\r'
        self.ser.write(message.encode())


if __name__ == '__main__':
    current_data = []

    Arduino = ArduinoCommunicator()

    for i in range(100):
        print(Arduino.RequestData('A0?\n'))
        #current_data.append(Arduino.RequestData('A0?'))

    time.sleep(100)
    Arduino.Tell('A0? -stream 10000')







# current_data = []
# data_count = 100
#
# for i in range(data_count):
#     serial_string = ser.readline()
#     serial_data = float(serial_string[-8:-2])
#     print(serial_data)
#     current_data.append(serial_data)
#
# ser.close()
#
# time = np.linspace(0, data_count, num=data_count, endpoint=False) * 100
# print(time)
# plot2D_x_y(time, current_data, name='Measured current', xlabel='time ms')



