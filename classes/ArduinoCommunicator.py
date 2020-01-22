import json
import serial
import time

class ArduinoCommunicator:

    def __init__(self, port='/dev/cu.usbserial-1410'):
        """
        Initializes the serial connection and receives the status data
        which is then stored in a public member of the class.

        :param port: serial port of arduino
        """
        print('STATUS : Starting connection...')
        self.conn_closed = False
        self.ser = serial.Serial(
            port=port,
            baudrate=9600,
            timeout=1
        )

        time.sleep(3)

        # parity = serial.PARITY_ODD,
        # stopbits = serial.STOPBITS_TWO,
        # bytesize = serial.SEVENBITS,

        try:
            status = json.loads(self._request('Status?', sleep=2))
        except json.decoder.JSONDecodeError as e:
            print("Status data could not be resolved.\n"
                  "Check if the data was received completely by increasing sleep and try again \n\n")
            raise e

        self.mean_delay = status['mean delay']
        self.stream_delay = status['stream delay']
        self.resistance = status['resistance']

        print('STATUS : Connected!')

    def __del__(self):
        if self.conn_closed:
            self.ser.close()
            self.conn_closed = True
        else:
            pass

    def __enter__(self):
        return self

    def __exit__(self):
        self.ser.close()
        self.conn_closed = True

    def _request(self, message:str, bytecount=None, sleep=1):
        """
        Sends a string to arduino and returns the message received.
        It waits for a specified amount of bytes.

        :comments:
        The function 'serial.in_waiting' is compatible with pyserial version 3 and above.
        Use 'serial.inWaiting()' instead for a pyserial version below 3.

        :param message: str command to arduino
        :param bytecount: expected bytecount of response
        :param sleep: amount of seconds to wait for response, if no bytecount is specified
        :return response: String of response
        """
        self.ser.write(message.encode())

        if bytecount is not None:
            while self.ser.in_waiting < bytecount:
                pass
                #print(self.ser.in_waiting)
        else:
            time.sleep(sleep)

        response = self.ser.readline().decode()
        if response[:5] == 'ERROR':
            raise Exception('Arduino reported Error: ' + response[8:])

        return response

    def _get_first_value(self, response:str):
        """
        gets the first numerical value after a ':' in a String.

        :param response: String which contains the value
        :return: (float, str) the extracted value, a substring of the input
                              which contains everything behind the number extracted
        """

        index_in = response.find(':') + 2
        if index_in == 1:
            raise IndexError('No valid data found in response from arduino. In index')
        index_out = index_in + 4

        result = float(response[index_in:index_out])
        response = response[index_in:]

        return result, response

    def Request_AD(self, mean_count=0):
        """
        Reads current from arduino.

        :param mean_count:
        :return: float with current
        """
        if mean_count == 1:
            response = self._request("AD?", bytecount=8)
        elif mean_count > 1:
            response = self._request("AD? -mean " + str(mean_count), bytecount=32)
        else:
            raise Exception('Invalid! mean count must be positive, but is: ' + str(mean_count))

        data, _ = self._get_first_value(response)
        return data


    def Request_V1_AD(self, mean_count=1):
        """
        Reads voltage 1 and current from arduino.

        :param mean_count: int
        :return: tuple with (float, float) (voltage 1, current)
        """
        if mean_count == 1:
            response = self._request("V1? AD?", bytecount=20)
        elif mean_count > 1:
            response = self._request("V1? -mean " + str(mean_count) +
                                     " AD? -mean " + str(mean_count), bytecount=32)
        else:
            raise Exception('Invalid! mean count must be positive, '
                            'but is: ' + str(mean_count))

        result = []
        for i in range(2):
            data, response = self._get_first_value(response)
            result.append(data)

        return result[0], result[1]

    def Request_V0_V1_AD(self, mean_count=1):
        """
        Reads both voltages and current from arduino.

        :param mean_count:
        :return: tuple (float, float, float) with (voltage 0, voltage 1, current)
        """
        if mean_count == 1:
            response = self._request("V0? V1? AD?", bytecount=29)
        elif mean_count > 1:
            response = self._request("V0? -mean " + str(mean_count) +
                                     " V1? -mean " + str(mean_count) +
                                     " AD? -mean " + str(mean_count), bytecount=72)
        else:
            raise Exception('Invalid! mean count must be positive, but is: ' + str(mean_count))

        result = []
        for i in range(3):
            data, response = self._get_first_value(response)
            result.append(data)

        return result[0], result[1], result[2]



if __name__ == "__main__":
    """This is some testing code."""

    Arduino = ArduinoCommunicator()

    print("started!")

    volt1, curr = Arduino.Request_V1_AD(1)
    print("V1={:2f} A={:2f}".format(volt1, curr))
    volt1, curr = Arduino.Request_V1_AD(2)
    print("V1={:2f} A={:2f}".format(volt1, curr))


    volt0, volt1, curr = Arduino.Request_V0_V1_AD(1)
    print("V0={:2f} V1={:2f}  A={:2f}".format(volt0, volt1, curr))
    volt0, volt1, curr = Arduino.Request_V0_V1_AD(2)
    print("V0={:2f} V1={:2f}  A={:2f}".format(volt0, volt1, curr))