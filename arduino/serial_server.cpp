#include <Arduino.h>

#include "serial_server.h"
#include "eeprom_controller.h"
#include "serial_interface.h"

#define SYN ('s')
#define ACK ('a')
#define ERR ('e')
#define RST ('r')
#define FIN ('f')
#define BYE ('b')

SerialServer::SerialServer(SerialInterface* interface) {
  this->interface = interface;
  this->isConnected = false;
  /* 256 is the amount of different ids allowed by int8_t. */
  this->handlersVector = (request_handler*) malloc(256);
  for (int i = 0; i < 255; i++) {
    this->handlersVector[i] = NULL;
  }
}

SerialServer::~SerialServer() {
  this->interface = NULL;
  free(this->handlersVector);
  this->handlersVector = NULL;
}

void SerialServer::Init() { 
  // Wait until the arduino is connected to the USB serial port.
  while (!interface->IsConnected()) {
    delay(200);
  }
}

void SerialServer::waitForConnection() {
  if (this->isConnected) {
    return;
  }
  
  while (true) {
    // Wait for a connect syn byte.
    if (!this->interface->WaitForBytes(1, 1000)) {
      continue;
    }

    // Read the syn.
    int8_t recv_byte = this->interface->Read_i8();
    if (SYN == recv_byte) {
      this->interface->Write_i8(ACK);
      this->isConnected = true;
      break;
    } 
    else {
      this->interface->Write_i8(RST);
    }
  }
}

void SerialServer::Serve() {
  if (!this->isConnected) {
    this->waitForConnection();
  }

  this->interface->WaitForBytes(1, 1000);
  if (this->interface->Available()) {
    /* Read the next handler id from the interface. */
    int8_t handler_id = interface->Read_i8();

    /* This is a special command to close the connection. */
    if (handler_id == BYE) {
      this->interface->Write_i8(BYE);
      this->isConnected = false;
      return;
    }

    /* Get the handler and execute it. */
    request_handler handler = this->handlersVector[handler_id];
    if (handler != NULL) {
      this->interface->Write_i8(ACK);
      handler(this->interface);
      this->interface->Write_i8(FIN);
    }
    else {
      /* No handler was found, terminate the session. */
      this->interface->Write_i8(ERR);
      this->isConnected = false;
    }
  }
  else {
    delay(20);
  }
}

void SerialServer::RegisterHandler(int8_t id, request_handler handler) {
  this->handlersVector[id] = handler;
}
