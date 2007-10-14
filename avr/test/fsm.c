/*!
* \file fsm.c
* \brief FSM for incomming data processing
*
*  URL: http://robotika.cz/
*  
*  Revision: 1.0
*  Date: 2006/01/29
*/

#include <string.h>

#include "global.h"
#include "uart.h"

#include "fsm.h"

// message processing machine state
 enum FsmStateEnum  {
FSM_WAIT_FOR_START = 1,
FSM_WAIT_FOR_CONTROL,
FSM_WAIT_FOR_ADDR_BYTE_3,
FSM_WAIT_FOR_ADDR_BYTE_2,
FSM_WAIT_FOR_ADDR_BYTE_1,
FSM_WAIT_FOR_ADDR_BYTE_0,
FSM_WAIT_FOR_LENGTH,
FSM_WAIT_FOR_DATA,
FSM_WAIT_FOR_CHECKSUM,
FSM_WAIT_FOR_STOP
};

// packet special character prefix and shift
#define FSM_PACKET_SPECIAL 0x00
#define FSM_PACKET_SPECIAL_SHIFT 0x04
// packet start byte
#define FSM_PACKET_START 0x02
// packet stop byte
#define FSM_PACKET_STOP 0x03

// max character being prefixed
#define FSM_PACKET_MAX_SPECIAL FSM_PACKET_STOP

// value added to the address while composing the reply	
#define FSM_REPLY_MASK 0x80

static uint8_t handlingSpecial = 0;

static volatile enum FsmStateEnum fsmState;
static uint8_t volatile dataLength;
static uint8_t volatile receivedAddress;
static uint8_t volatile checkSum;

static uint8_t volatile correctLength;

static uint8_t volatile dataReceived;

typedef uint8_t (*uint8FuncPtrDataSize)(uint8_t*, uint8_t);
volatile static uint8FuncPtrDataSize commandFunction;

// data buffer
uint8_t dataBuffer[ROBBUS_RX_BUFFER_MAX_SIZE];

// forward declarations
void doCommand(void);
void fsmProcessByte(uint8_t data);

uint8_t emptyFunction(uint8_t *data, uint8_t data_size) { 
	return 0; 
}

#define checkSumInit() checkSum = 0
#define checkSumAdd(data) checkSum += data;

//! initialize FSM
void fsmInit(uint8_t (*cmd_func)(uint8_t*, uint8_t)) {
	uartInit();
	uartSetBaudRate(115200);

	fsmState = FSM_WAIT_FOR_START;
	handlingSpecial = 0;

	// register Rx handler
	uartSetRxHandler(fsmProcessByte);
	fsmSetCommandHandler(cmd_func);
}

//! redirects command processing to a user function
void fsmSetCommandHandler(uint8_t (*cmd_func)(uint8_t*, uint8_t)) {
	// set the receive interrupt to run the supplied user function
	if (cmd_func)
		commandFunction = cmd_func;
	else
		commandFunction = emptyFunction;
}

//! process incoming byte
void fsmProcessByte(uint8_t data) {

	// handle special character
	if (data == FSM_PACKET_SPECIAL) {	// special character received, set flag, do not change state
		handlingSpecial = 1;
		return;
	}

	if (handlingSpecial) {			// previous was special, so shift accordingly
		handlingSpecial = 0;
		data -= FSM_PACKET_SPECIAL_SHIFT;
	}

	// checking start byte is outside the fsm (because of synchronizing)
	if (data == FSM_PACKET_START) {
		fsmState = FSM_WAIT_FOR_CONTROL;
		checkSumInit(); // initialize checksum counter
		return;
	}
	
	switch (fsmState) {	
		case FSM_WAIT_FOR_CONTROL:
			if (data & FSM_REPLY_MASK) {
				fsmState = FSM_WAIT_FOR_START; // reply from someone, ignore rest of packet
			} else {
				checkSumAdd(data);
				fsmState = FSM_WAIT_FOR_ADDR_BYTE_3;
			}
			break;


		case FSM_WAIT_FOR_ADDR_BYTE_3:
			if (data == ROBBUS_ADDR_BYTE_3) {
				checkSumAdd(data);
				fsmState = FSM_WAIT_FOR_ADDR_BYTE_2; // for me
			} else {
				fsmState = FSM_WAIT_FOR_START; // for someone else
			}
			break;
		
		case FSM_WAIT_FOR_ADDR_BYTE_2:
			if (data == ROBBUS_ADDR_BYTE_2) {
				checkSumAdd(data);
				fsmState = FSM_WAIT_FOR_ADDR_BYTE_1; // for me
			} else {
				fsmState = FSM_WAIT_FOR_START; // for someone else
			}
			break;
		
		case FSM_WAIT_FOR_ADDR_BYTE_1:
			if (data == ROBBUS_ADDR_BYTE_1) {
				checkSumAdd(data);
				fsmState = FSM_WAIT_FOR_ADDR_BYTE_0; // for me
			} else {
				fsmState = FSM_WAIT_FOR_START; // for someone else
			}
			break;
		
		case FSM_WAIT_FOR_ADDR_BYTE_0:
			if (data == ROBBUS_ADDR_BYTE_0) {
				checkSumAdd(data);
				fsmState = FSM_WAIT_FOR_LENGTH; // for me
			} else {
				fsmState = FSM_WAIT_FOR_START; // for someone else
			}
			break;
		
		case FSM_WAIT_FOR_LENGTH:
			checkSumAdd(data);
			dataLength = data; // ommit the opcode
			dataReceived = 0;
			fsmState = FSM_WAIT_FOR_DATA;
			break;

		case FSM_WAIT_FOR_DATA:
			if (dataReceived < ROBBUS_RX_BUFFER_MAX_SIZE) {
				dataBuffer[dataReceived] = data;
				checkSum += data;
				dataReceived++;
			}
			
			if (dataReceived == dataLength) {
				fsmState = FSM_WAIT_FOR_CHECKSUM;
			}	
			break;

		case FSM_WAIT_FOR_CHECKSUM:
			
			if (((uint8_t)(data + checkSum)) == 0) {
				fsmState = FSM_WAIT_FOR_STOP;
			} else {
				// wrong checkSum
				fsmState = FSM_WAIT_FOR_START;
			}
			break;
		
		case FSM_WAIT_FOR_STOP:
			
			if (data == FSM_PACKET_STOP) {
				doCommand();
			}
			
			fsmState = FSM_WAIT_FOR_START;
			break;

		default:
			// should never happen ;-)
		break;
	}
}

static void sendWrappedWithCheckSum(uint8_t data) {

	if (data > FSM_PACKET_MAX_SPECIAL)
		uartAddToTxBuffer(data);
	else {
		uartAddToTxBuffer(FSM_PACKET_SPECIAL);
		uartAddToTxBuffer(data + FSM_PACKET_SPECIAL_SHIFT);
	}

	checkSumAdd(data);
}

void doCommand(void) {
	// do action here
	uint8_t replyDataSize = commandFunction(dataBuffer, dataReceived);
	
	// send reply
	checkSumInit();
	uartAddToTxBuffer(FSM_PACKET_START);
	sendWrappedWithCheckSum(FSM_REPLY_MASK);
	sendWrappedWithCheckSum(ROBBUS_ADDR_BYTE_3);
	sendWrappedWithCheckSum(ROBBUS_ADDR_BYTE_2);
	sendWrappedWithCheckSum(ROBBUS_ADDR_BYTE_1);
	sendWrappedWithCheckSum(ROBBUS_ADDR_BYTE_0);
	sendWrappedWithCheckSum( replyDataSize );

	uint8_t index = 0; 

	while (index < replyDataSize) {
		sendWrappedWithCheckSum( dataBuffer[index++] );
	}

	uartAddToTxBuffer(-checkSum);
	uartAddToTxBuffer(FSM_PACKET_STOP);

	uartSendTxBuffer();
}


