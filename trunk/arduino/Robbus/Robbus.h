/*
  Robbus.h - Library for Robbus communication protocol.
  Created by Kamil Rezac, October 18, 2011.
  Released into the public domain.
*/
#ifndef Robbus_h
#define Robbus_h

#include "WProgram.h"

class RobbusLib
{
	public:
		RobbusLib();
		void begin(byte address, byte inDataSize, byte outDataSize, byte* (*)(byte*));
		void process();
	private:
		// data fields
		byte* (*commandHandler)(byte*);
		byte robbusState;    //! state of the processing state machine
		byte payloadLength;
		byte checkSum;
		byte deviceAddress;
		byte* usartBuffer;
		byte usartBufferSize;
		byte usartBufferIndex;
		byte incomingDataSize;
		byte outgoingDataSize;

		// private functions
		byte doServiceCommand(void);
		byte sendWrapped(byte c);		
};

  // "singleton"
  extern RobbusLib Robbus;
#endif