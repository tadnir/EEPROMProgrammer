#include <Arduino.h>

#include "eeprom_controller.h"

#define SHIFT_CLK 2
#define SHIFT_LATCH 3 
#define SHIFT_DATA 4
#define EEPROM_D0 5
#define EEPROM_D7 12
#define WRITE_EN 13


EEPROMController::EEPROMController() {
  this->maxAddress = 0x07ff;
}

void EEPROMController::setAddress(int16_t address, bool outputEnable) {
  /* We will shift our 2bytes as MSBFIRST.
   * This means that we need to push the high byte first in MSBFIRST mode,
   * and then push the low byte in MSBFIRST mode too.
   * Note that the highest bit is used as outputEnable which is ActiveLow. */
  shiftOut(SHIFT_DATA, SHIFT_CLK, MSBFIRST, (address >> 8) | (outputEnable ? 0x00 : 0x80));
  shiftOut(SHIFT_DATA, SHIFT_CLK, MSBFIRST, address);

  digitalWrite(SHIFT_LATCH, LOW);
  digitalWrite(SHIFT_LATCH, HIGH);
  digitalWrite(SHIFT_LATCH, LOW);
}

void EEPROMController::setDataPinsMode(int mode) {
  for (int pin = EEPROM_D0; pin <= EEPROM_D7; pin += 1) {
    pinMode(pin, mode);
  }
}

void EEPROMController::initPin(int pin, int mode, int defaultValue) {
  if (mode == OUTPUT) {
    digitalWrite(pin, defaultValue);
  }
  
  pinMode(pin, mode);
}

void EEPROMController::Init() {
  // Set the default modes for the IO pins.
  this->initPin(SHIFT_DATA,  OUTPUT, LOW);
  this->initPin(SHIFT_CLK,   OUTPUT, LOW);
  this->initPin(SHIFT_LATCH, OUTPUT, LOW);
  this->initPin(WRITE_EN,    OUTPUT, HIGH);
  this->setDataPinsMode(INPUT);

  // Zero the address shift registers.
  this->setAddress(0x0000, true);
}

byte EEPROMController::Read(int16_t address) {
  this->setDataPinsMode(INPUT);
  this->setAddress(address, true);
  byte data = 0;
  for (int pin = EEPROM_D7; pin >= EEPROM_D0; pin -= 1) {
    data = (data << 1) + digitalRead(pin);
  }

  return data;
}

void EEPROMController::Write(int16_t address, byte data) {
  /* The EEPROM has a limited number of write cycles, 
   * if we can prevent duplicate write we might as well do so to prolong it's life. */
  byte currentData = this->Read(address);
  if (currentData == data) {
    return;
  }
  
  this->setDataPinsMode(OUTPUT);
  this->setAddress(address, false);
  for (int pin = EEPROM_D0; pin <= EEPROM_D7; pin += 1) {
   digitalWrite(pin, data & 1);
   data = data >> 1;
  }

  digitalWrite(WRITE_EN, LOW);
  delayMicroseconds(1);
  digitalWrite(WRITE_EN, HIGH);
  delay(5);
}
