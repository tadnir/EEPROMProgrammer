#include <Arduino.h>

#include "eeprom_controller.h"
#include "serial_interface.h"
#include "serial_server.h"

#define SERIAL_RATE ((int) 9600)
#define SERIAL_TIMEOUT ((unsigned long) 20)


SerialInterface* interface = NULL;
EEPROMController* eeprom = NULL;
SerialServer* server = NULL;


void maxAddressHandler(SerialInterface* interface) {
  interface->Write_i16(eeprom->maxAddress);
}

void echoHandler(SerialInterface* interface) {
  int8_t bufSize = interface->Read_i8();
  byte* buffer = (byte*) malloc((size_t) bufSize);
  interface->ReadBuffer(buffer, bufSize);
  
  interface->Write_i8(bufSize);
  interface->WriteBuffer(buffer, bufSize);
  free(buffer);
}

void readHandler(SerialInterface* interface) {
  int16_t address = interface->Read_i16();
  byte data = eeprom->Read(address);
  interface->Write_i8((int8_t) data);
}

void writeHandler(SerialInterface* interface) {
  int16_t address = interface->Read_i16();
  byte data = (byte) interface->Read_i8();
  eeprom->Write(address, data);
}

void readBufferHandler(SerialInterface* interface) {
  int16_t address = interface->Read_i16();
  size_t length = (size_t) interface->Read_i8();
  byte* buffer = (byte*) malloc(length);
  for (size_t i = 0; i < length; i++) {
    buffer[i] = eeprom->Read(address + ((int16_t) i));
  }
  
  interface->WriteBuffer(buffer, length);
  free(buffer);
}

void writeBufferHandler(SerialInterface* interface) {
  int16_t address = interface->Read_i16();
  size_t length = (size_t) interface->Read_i8();
  byte* buffer = (byte*) malloc(length);
  interface->ReadBuffer(buffer, length);
  for (size_t i = 0; i < length; i++) {
    eeprom->Write(address + ((int16_t) i), buffer[i]);
  }
  
  free(buffer);
}

void setup() {
  eeprom = new EEPROMController();
  interface = new SerialInterface(SERIAL_RATE, SERIAL_TIMEOUT);
  server = new SerialServer(interface);

  eeprom->Init();
  server->Init();

  server->RegisterHandler('m', maxAddressHandler);
  server->RegisterHandler('e', echoHandler);
  server->RegisterHandler('r', readHandler);
  server->RegisterHandler('w', writeHandler);
  server->RegisterHandler('R', readBufferHandler);
  server->RegisterHandler('W', writeBufferHandler);
}


void loop() {
  server->Serve();
}
