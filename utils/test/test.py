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

def sendMessage(ser,address,data):
	sum = 0;
	ser.write("\x02")     #write packet start
	sum = sendWrapped(ser,"\x00",sum)
	for c in address:
		sum = sendWrapped(ser,c,sum) 
	sum = sendWrapped(ser,chr(len(data)),sum)
	for c in data:
		sum = sendWrapped(ser,c,sum)	
	outSum = (256-(sum % 256)) % 256
	sendWrapped(ser,chr(outSum),sum)
	ser.write("\x03")     #write a string

# read reply
def readReply(ser):
	# consume outgoing message
	print "Consuming sent data..."
	while True:
		x = ser.read(1)
		if x == "\x03":
			break
	
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
	if len(argv) < 2:
		print "Usage: test.py address [data]"
		print "Both address and data are read as hexa values if"
		print "prefixed with \\x (or \\\\x to avoid shell expansion)"
		print "Example (bash): ./test.py KRT1 \\\\x0305"
		return
	
	ser = serial.Serial('/dev/robbus', 115200, timeout=1)
	if argv[1][0:2] == "\\x":
		print "Decoding hex address"
		address = argv[1][2:].decode("hex");
	else:
		address = argv[1];
	if len(address) != 4:
		print "Address must have 4 bytes"
		return
	data = None;
	if len(argv) > 2:
		if argv[2][0:2] == "\\x":
			print "Decoding hex data"
			data = argv[2][2:].decode("hex");
		else:
			data = argv[2];
	else:
		data = ""
	print "Sending..."
	sendMessage(ser,address,data)
	parseReply(readReply(ser))
	ser.close()

if __name__ == "__main__":
	from sys import argv
	main(argv)
