#include "eeprom_controller"
#include "serial_interface"
#include "serial_server"

#define SERIAL_RATE ((int) 9600)
#define SERIAL_TIMEOUT ((unsigned long) 20)

SerialInterface* interface = null;
EEPROMController* eeprom = null;
SerialServer* server = null;

void readHandler(SerialInterface* interface) {
  int16_t address = interface->Read_i16();
  byte data = eeprom->Read(address);
  interface->Write_i8((int8_t) data);
}

void setup() {
  eeprom = new EEPROMController();
  interface = new SerialInterface(SERIAL_RATE, SERIAL_TIMEOUT);
  server = new SerialServer(interface);

  eeprom->Init();
  server->Init();

  server->RegisterHandler('r', readHandler);
}


void loop() {
  server->Serve();
}
