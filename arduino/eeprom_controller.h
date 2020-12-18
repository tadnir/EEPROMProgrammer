
#ifndef EEPROM_CONTROLLER_H
#define EEPROM_CONTROLLER_H

#include <Arduino.h>

class EEPROMController {
  private:
    void setAddress(int16_t address, bool outputEnable);
    void setDataPinsMode(int mode);
    void initPin(int pin, int mode, int defaultValue);
  public:
    int16_t maxAddress;
  
    EEPROMController();
    void Init();
    byte Read(int16_t address);
    void Write(int16_t address, byte data);
};

typedef class EEPROMController EEPROMController;

#endif /* EEPROM_CONTROLLER_H */
