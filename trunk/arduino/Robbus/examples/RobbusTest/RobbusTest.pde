#include <Robbus.h>

byte outData[2];

byte* robbusHandler(byte* data)
{
  outData[0] = 'K';
  outData[1] = data[0];
  return outData;
}

void setup()
{
  // parameters: address, indata size, outdata size, handler
  Robbus.begin('a', 1, 2, robbusHandler);  
}

void loop()
{
  Robbus.process();
}
