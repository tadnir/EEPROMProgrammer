#ifndef SERIAL_SERVER_H
#define SERIAL_SERVER_H

#include <Arduino.h>
#include "eeprom_controller.h"
#include "serial_interface.h"

typedef void (*request_handler)(SerialInterface* interface);

class SerialServer {
  private:
    SerialInterface* interface;
    request_handler* handlersVector;
    bool isConnected;
    void waitForConnection();
  public:
    SerialServer(SerialInterface* interface);
    ~SerialServer();
    void Init();
    void RegisterHandler(int8_t id, request_handler handler);
    void Serve();
};

typedef class SerialServer SerialServer;

#endif /* SERIAL_SERVER_H */
