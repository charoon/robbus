/*
  Robbus.h - Library for Robbus communication protocol.
  Created by Kamil Rezac, October 18, 2011.
  Released into the public domain.
*/
#ifndef Robbus_h
#define Robbus_h

#include "WProgram.h"

// abstract parent class for communication wrappers
class RobbusCommWrapper
{
	public:
		RobbusCommWrapper() {}
		virtual void begin() = 0;
		virtual int available() = 0;
		virtual int read() = 0;
		virtual void write(uint8_t) = 0;

};

class RobbusLib
{
	public:
		RobbusLib();
		void begin(RobbusCommWrapper* commWrapperPtr, byte address, byte inDataSize, byte outDataSize, byte* (*)(byte*));
		void process();
	private:
		// data fields
		RobbusCommWrapper* commWrapper;
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

#if defined(UBRRH) || defined(UBRR0H)
class RobbusCommWrapper_Serial : public RobbusCommWrapper
{
	public:
		RobbusCommWrapper_Serial() { }
		virtual void begin() { Serial.begin(115200); }
		virtual int available() { return Serial.available(); }
		virtual int read() { return Serial.read(); }
		virtual void write(uint8_t data) { Serial.write(data); }
};
#endif

#if defined(UBRR1H)
class RobbusCommWrapper_Serial1 : public RobbusCommWrapper
{
	public:
		RobbusCommWrapper_Serial1() { }
		virtual void begin() { Serial1.begin(115200); }
		virtual int available() { return Serial1.available(); }
		virtual int read() { return Serial1.read(); }
		virtual void write(uint8_t data) { Serial1.write(data); }
};
#endif

#if defined(UBRR2H)
class RobbusCommWrapper_Serial2 : public RobbusCommWrapper
{
	public:
		RobbusCommWrapper_Serial2() { }
		virtual void begin() { Serial2.begin(115200); }
		virtual int available() { return Serial2.available(); }
		virtual int read() { return Serial2.read(); }
		virtual void write(uint8_t data) { Serial2.write(data); }
};
#endif

#if defined(UBRR3H)
class RobbusCommWrapper_Serial3 : public RobbusCommWrapper
{
	public:
		RobbusCommWrapper_Serial3() { }
		virtual void begin() { Serial3.begin(115200); }
		virtual int available() { return Serial3.available(); }
		virtual int read() { return Serial3.read(); }
		virtual void write(uint8_t data) { Serial3.write(data); }
};
#endif

#endif