#ifndef SERIAL_INTERFACE_H
#define SERIAL_INTERFACE_H

#include <Arduino.h>

class SerialInterface {
  private:
    unsigned long timeout;
  public:
    SerialInterface(int serial_rate, unsigned long timeout);
    bool IsConnected();
    void SetRecvTimout(unsigned long timeout);

    int64_t Available();
    bool WaitForBytes(size_t num_bytes, unsigned long timeout);

    void ReadBuffer(byte* buffer, size_t size);
    int8_t Read_i8();
    int16_t Read_i16();
    int32_t Read_i32();

    void WriteBuffer(byte* buffer, size_t size);
    void Write_i8(int8_t data);
    void Write_i16(int16_t data);
    void Write_i32(int32_t data);

    void println(const char* str);
    void print(const char* str);
};

typedef class SerialInterface SerialInterface;

#endif /* SERIAL_INTERFACE_H */
