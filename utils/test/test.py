import serial
import time
# Open named port at "19200,8,N,1", 1s timeout
ser = serial.Serial('/dev/robbus', 115200, timeout=1)
#buffer = [0x02,ord('K'),ord('R'),ord('T'),ord('1'),0x01,0x05,216,0x03]
buffer = [chr(0x02)]
#print buffer
#souc = 0
#for i in buffer:
#	souc += i
#print 512-souc
#buffer = [chr(i) for i in buffer]
#print buffer
ser.write("\x02")     #write a string
ser.write("\x00")     #write a string
ser.write("\x04")     #write a string
ser.write("K")     #write a string
ser.write("R")     #write a string
ser.write("T")     #write a string
ser.write("1")     #write a string
ser.write("\x00")     #write a string
ser.write("\x05")     #write a string
ser.write("\x05")     #write a string
ser.write("\xd8")     #write a string
ser.write("\x03")     #write a string
s = ser.read(50)        #read up to ten bytes (timeout)
print len(s)
print [ord(i) for i in s]
ser.close()

