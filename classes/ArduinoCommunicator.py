import json
import serial
import time

class ArduinoCommunicator:
    def __init__(self, port='/dev/cu.usbserial-1410'):
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

    def _request(self, message, bytecount=None, sleep=1):
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

        #print(response)
        return response

    def RequestData(self, message):
        response = self._request(message, bytecount=32)
        index_in = response.find(':') + 2
        if index_in == 1:
            #this happens, when : does not exist in string, find() returns -1
            raise IndexError('No valid data found in response from arduino. In index')
        index_out = index_in + 4
        # index_out = index_in + response[index_in:].find(' ')
        # if index_out == -1:
        #     raise IndexError('No valid data found in response from arduino. Out index')
        return float(response[index_in:index_out])

    def Receive(self):
        return self.ser.readline()

    def Tell(self, message):
        message = message + '\n\r'
        self.ser.write(message.encode())

    def RequestAD(self, mean_count=0):
        if mean_count == 1:
            response = self._request("AD?", bytecount=8)
        elif mean_count > 1:
            response = self._request("AD? -mean " + str(mean_count), bytecount=32)
        else:
            raise Exception('Invalid! mean count must be positive, but is: ' + str(mean_count))

        index_in = response.find(' ')
        if index_in == -1:
            raise IndexError('No valid data found in response from arduino. In index')
        index_out = index_in + 4
        return float(response[index_in:index_out])


    def RequestV1AD(self, mean_count=1):
        if mean_count == 1:
            response = self._request("V1? AD?", bytecount=20)
        elif mean_count > 1:
            response = self._request("V1? -mean " + str(mean_count) + " AD? -mean " + str(mean_count), bytecount=32)
        else:
            raise Exception('Invalid! mean count must be positive, but is: ' + str(mean_count))

        result = []

        for i in range(2):
            index_in = response.find(':') + 2
            if index_in == -1:
                raise IndexError('No valid data found in response from arduino. In index')
            index_out = index_in + 4

            result.append(float(response[index_in:index_out]))
            response = response[index_in:]

        return result[0], result[1]

    def RequestV0V1AD(self, mean_count=1):
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
            index_in = response.find(':') + 2
            if index_in == -1:
                raise IndexError('No valid data found in response from arduino. In index')
            index_out = index_in + 4

            result.append(float(response[index_in:index_out]))
            response = response[index_in:]

        return result[0], result[1], result[2]



if __name__ == "__main__":
    Arduino = ArduinoCommunicator()

    print("started!")

    volt1, curr = Arduino.RequestV1AD(1)
    print("V1={:2f} A={:2f}".format(volt1, curr))
    volt1, curr = Arduino.RequestV1AD(2)
    print("V1={:2f} A={:2f}".format(volt1, curr))


    volt0, volt1, curr = Arduino.RequestV0V1AD(1)
    print("V0={:2f} V1={:2f}  A={:2f}".format(volt0, volt1, curr))
    volt0, volt1, curr = Arduino.RequestV0V1AD(2)
    print("V0={:2f} V1={:2f}  A={:2f}".format(volt0, volt1, curr))