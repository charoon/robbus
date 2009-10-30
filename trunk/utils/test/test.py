#!/usr/bin/python

import serial
import time

def sendWrapped(ser,c, sum):
	if ord(c) < 4:
		ser.write("\x00")
		d = chr(ord(c)+4)
		ser.write(d)
	else:
		ser.write(c)
	return sum+ord(c)

def sendMessage(ser,alias,data,mask):
	sum = 0;
	if mask is None:
		ser.write("\x02")     #write regular packet start
	else:
		ser.write("\x03")     #write group packet start
	sum = sendWrapped(ser,alias,sum) 
	if mask is not None:
		sum = sendWrapped(ser,mask,sum) 	
	sum = sendWrapped(ser,chr(len(data)),sum)
	for c in data:
		sum = sendWrapped(ser,c,sum)	
	outSum = (256-(sum % 256)) % 256
	sendWrapped(ser,chr(outSum),sum)

def dewrap_read(ser):
	x = ser.read(1)
	if ord(x) == 0:
		return chr(ord(ser.read(1))-4)
	else:
		return x

# read reply
def readReply(ser):
	# consume outgoing message
	s = ""
	print "Consuming sent data..."
	x = ser.read(1)
	print x, ord(x)
	while True:
		x = ser.read(1)
		print x, ord(x)
		if len(x) == 0 or ( ord(x) > 0 and ord(x) < 4):
			#print "break"
			#s += x
			break
	
	# and read incomming
	print "Receiving data..."
	s += ser.read(1) # return adress, no need to dewrap
	lenstr = dewrap_read(ser)
	paylen = ord(lenstr);
	s += lenstr
	while paylen > 0:
		s += dewrap_read(ser);
		paylen = paylen-1
	s += ser.read(1) #chsum
	return s

def parseReply(s):
	if len(s) < 2:
		print "Input too short"
		return
	#s = s [1:-1] # cut start and stop
	chSum = sum([ord(c) for c in s]) 
	if sum([ord(c) for c in s]) % 256 != 0:
		print "Invalid checksum", (chSum%256), (256-(chSum%256))
		return -1
	address = chr(ord(s[0]) - 128)
	print "Reply from:", address, " hex:", address.encode("hex")
	replySize = ord(s[1])
	print "      size:", replySize
	if replySize != len (s[2:-1]):
		print "Data size doesn't match real data length"
	data = s[2:-1]
	print "      data:", [ord(i) for i in data], " hex:", data.encode("hex")
	return 0


def main(argv = None):
	if len(argv) < 3:
		print "Usage: test.py address data [mask]"
		print "All address, data and mask are read as hexa values if"
		print "prefixed with \\x (or \\\\x to avoid shell expansion)"
		print "Example (bash): ./test.py KRT1 \\\\x0305"
		return
	
	ser = serial.Serial('/dev/robbus', 115200, timeout=1)
	if argv[1][0:2] == "\\x":
		print "Decoding hex address"
		address = argv[1][2:].decode("hex");
	else:
		address = argv[1];
	if len(address) != 1:
		print "Address must have 1 byte"
		return
	if argv[2][0:2] == "\\x":
		print "Decoding hex data"
		data = argv[2][2:].decode("hex");
	else:
		data = argv[2];
	if len(argv) > 3:
		if argv[3][0:2] == "\\x":
			print "Decoding hex mask"
			mask = argv[3][2:].decode("hex");
		else:
			mask = argv[3];
		if len(mask) != 1:
			print "Mask must have 1 byte"
			return
	else:
		mask = None
	print "Sending..."
	sendMessage(ser,address,data,mask)
	ret = parseReply(readReply(ser))
	ser.close()
	return ret

if __name__ == "__main__":
	from sys import argv
	main(argv)
