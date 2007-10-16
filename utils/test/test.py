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

# read reply
def readReply(ser):
	# consume outgoing message
	print "Consuming sent data..."
	while True:
		x = ser.read(1)
		print x, ord(x)
		#if x == "\x03":
		#	break
	
	# and read incomming
	print "Receiving data..."
	s = ""
	while True:
		x = ser.read(1)
		s += x
		if x == "\x03":
			break
	print "Packet received..."
	return s

def dewrap(s):
	out = ""
	special = False
	for c in s:
		if special:
			special = False
			out += chr(ord(c) - 4)
		elif ord(c) == 0:
			special = True
		else:
			out += c
	return out

def parseReply(s):
	s = s [1:-1] # cut start and stop
	s = dewrap(s)
	chSum = sum([ord(c) for c in s]) 
	if sum([ord(c) for c in s]) % 256 != 0:
		print "Invalid checksum"
	address = s[1:5]
	print "Reply from:", address, " hex:", address.encode("hex")
	replySize = ord(s[5])
	print "      size:", replySize
	if replySize != len (s[6:-1]):
		print "Data size doesn't match real data length"
	data = s[6:-1]
	print "      data:", [ord(i) for i in data], " hex:", data.encode("hex")


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
	parseReply(readReply(ser))
	ser.close()

if __name__ == "__main__":
	from sys import argv
	main(argv)
