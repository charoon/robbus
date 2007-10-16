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

def sendMessage(ser,start,address,alias):
	sum = 0;
	ser.write(start)     #write packet start
	sum = sendWrapped(ser,alias,sum)
	for c in address:
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
	
def main(argv = None):
	if len(argv) != 4:
		print "Usage: alias.py op address alias"
		print "op is a (acquire) or r (release)"
		print "Both address and alias are read as hexa values if"
		print "prefixed with \\x (or \\\\x to avoid shell expansion)"
		print "Example (bash): ./alias.py KRETE1 \\\\x01"
		return
	
	ser = serial.Serial('/dev/robbus', 115200, timeout=1)
	
	start = "x"
	if argv[1][0] == "a":
		start = "\x01"
	elif argv[1][0] == "r":
		start = "\x03"
	else:
		print "op must be either \"a\" or \"r\""
		return
	if argv[2][0:2] == "\\x":
		print "Decoding hex address"
		address = argv[2][2:].decode("hex");
	else:
		address = argv[2];
	if len(address) != 6:
		print "Address must have 6 bytes"
		return
	
	if argv[3][0:2] == "\\x":
		print "Decoding hex alias"
		alias = argv[3][2:].decode("hex");
	else:
		alias = argv[3];
	if len(alias) != 1:
		print "Alias must have 1 byte"
		return
	
	print "Sending..."
	sendMessage(ser,start,address,alias)
	readReply(ser)
	ser.close()

if __name__ == "__main__":
	from sys import argv
	main(argv)
