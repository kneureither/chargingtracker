import time
import serial

ser = serial.Serial(
            port='/dev/cu.usbserial-1410',
            baudrate=9600,
            timeout=1
        )

time.sleep(3)

ser.write('A0?\n'.encode())
time.sleep(0.5)
response = ser.readline().decode()
print(response)
#value = float(response[4:8])
#print(value)
time.sleep(10)
ser.close()