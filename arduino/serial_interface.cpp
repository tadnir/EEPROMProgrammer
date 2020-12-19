#include <Arduino.h>

#include "serial_interface.h"

SerialInterface::SerialInterface(int serial_rate, unsigned long timeout) {
  this->timeout = timeout;
  Serial.begin(serial_rate);
  Serial.setTimeout(this->timeout);
}

bool SerialInterface::IsConnected() {
  if (Serial) {
    return true;
  }
  else {
    return false;
  }
}

void SerialInterface::SetRecvTimout(unsigned long timeout) {
  this->timeout = timeout;
  Serial.setTimeout(this->timeout);
}

int64_t SerialInterface::Available() {
  return Serial.available();
}

bool SerialInterface::WaitForBytes(size_t num_bytes, unsigned long timeout) {
  unsigned long startTime = millis();
  //Wait for incoming bytes or exit if timeout
  while ((Serial.available() < num_bytes) && (millis() - startTime < timeout)){}
}

void SerialInterface::ReadBuffer(byte* buffer, size_t size) {
  this->WaitForBytes(size, this->timeout);
  byte data = 0;
  for (size_t i = 0; i < size; i++) {
    data = Serial.read();   
    buffer[i] = data;
  }
}

int8_t SerialInterface::Read_i8() {
  byte buffer[1];
  this->WaitForBytes(1, this->timeout);
  this->ReadBuffer(buffer, 1);
  return (int8_t) buffer[0];
}

int16_t SerialInterface::Read_i16() {
  byte buffer[2];
  this->WaitForBytes(2, this->timeout);
  this->ReadBuffer(buffer, 2);
  return (((int16_t) buffer[0]) << 0 & 0x00ff) | 
         (((int16_t) buffer[1]) << 8 & 0xff00);
}

int32_t SerialInterface::Read_i32() {
  byte buffer[4];
  this->WaitForBytes(4, this->timeout);
  this->ReadBuffer(buffer, 4);
  return (((int32_t) buffer[0]) << 0  & 0x000000ff) | 
         (((int32_t) buffer[1]) << 8  & 0x0000ff00) | 
         (((int32_t) buffer[2]) << 16 & 0x00ff0000) | 
         (((int32_t) buffer[3]) << 24 & 0xff000000);
}

void SerialInterface::WriteBuffer(byte* buffer, size_t size) {
  Serial.write(buffer, size);
}

void SerialInterface::Write_i8(int8_t data) {
  byte buffer[1] = {
    (byte) data
  };
  this->WriteBuffer(buffer, 1);
}

void SerialInterface::Write_i16(int16_t data) {
  byte buffer[2] = {
    (byte) ((data >> 0) & 0x00ff),
    (byte) ((data >> 8) & 0x00ff)
  };
  this->WriteBuffer(buffer, 2);
}

void SerialInterface::Write_i32(int32_t data) {
  byte buffer[4] = {
    (byte) ((data >> 0)  & 0x000000ff),
    (byte) ((data >> 8)  & 0x000000ff),
    (byte) ((data >> 16) & 0x000000ff),
    (byte) ((data >> 24) & 0x000000ff)
  };
  this->WriteBuffer(buffer, 4);
}

void SerialInterface::println(const char* str) {
  Serial.println(str);
  this->Write_i8(0);
}

void SerialInterface::print(const char* str) {
  Serial.print(str);
  this->Write_i8(0);
}
