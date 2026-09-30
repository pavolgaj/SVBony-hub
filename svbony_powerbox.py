import serial
import struct
import time
import sys, os

class SVBonyPowerBox:
    HEADER = 0x24
    BAUDRATE = 115200

    STATUS_FAILURE = 0xAA

    # Port mapping
    DC1 = 0
    DC2 = 1
    DC3 = 2
    DC4 = 3
    DC5 = 4

    USB_GROUP_1 = 5
    USB_GROUP_2 = 6

    REGULATED = 7

    PWM1 = 8
    PWM2 = 9

    def __init__(self, port, timeout=0.5):
        self.ser = serial.Serial(
            port=port,
            baudrate=self.BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout,
        )

    def close(self):
        self.ser.close()

    def flush(self):
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

    @staticmethod
    def checksum(data):
        '''
        Protocol checksum:
            sum(all bytes except checksum) % 255
        '''
        return sum(data) % 0xFF

    def send_command(self, payload, response_data_length):
        '''
        payload: bytes of command payload
        response_data_length:
            number of expected data bytes in response
        '''

        frame_length = len(payload) + 3

        frame = bytearray()
        frame.append(self.HEADER)
        frame.append(frame_length)
        frame.extend(payload)

        frame.append(self.checksum(frame))

        self.flush()

        self.ser.write(frame)
        self.ser.flush()

        time.sleep(0.1)

        response_length = 3 + response_data_length + 1

        response = self.ser.read(response_length)

        if len(response) != response_length:
            raise IOError(
                f"Incomplete response "
                f"(expected {response_length}, got {len(response)})"
            )

        if response[0] != self.HEADER:
            raise IOError(
                f"Invalid header: 0x{response[0]:02X}"
            )

        calc = self.checksum(response[:-1])

        if calc != response[-1]:
            raise IOError(
                f"Checksum mismatch "
                f"(expected 0x{calc:02X}, got 0x{response[-1]:02X})"
            )

        status = response[2]

        if status == self.STATUS_FAILURE:
            raise IOError("Device reported command failure")

        return response[3:-1]

    @staticmethod
    def decode_u32(data):
        '''
        Big-endian uint32
        '''
        return struct.unpack(">I", data)[0]

    #
    # Handshake
    #

    def handshake(self):
        '''
        Read status as communication test.
        '''

        try:
            self.get_status()
            return True
        except Exception:
            return False

    #
    # Write operations
    #

    def set_output(self, port, value):
        '''
        Generic output setter.

        value:
            0..255
        '''

        payload = bytes([0x01, port, value])

        self.send_command(payload, 2)

    def set_dc(self, channel, enabled):
        '''
        channel: 0..4
        '''

        port = channel #- 1

        self.set_output(port, 0xFF if enabled else 0x00)

    def set_usb(self, group, enabled):
        '''
        group: 0 or 1
        '''

        port = 5 + (group)

        self.set_output(port, 0xFF if enabled else 0x00)

    def set_pwm(self, channel, duty_percent):
        '''
        channel: 0 or 1

        duty_percent:
            0..100
        '''

        duty_percent = max(0, min(100, duty_percent))

        raw = round(255 * duty_percent / 100)

        port = 8 + (channel)

        self.set_output(port, raw)

    def set_regulated_voltage(self, voltage):
        '''
        0.0-15.3 V
        '''

        voltage = max(0.0, min(15.3, voltage))

        raw = round(voltage * 255 / 15.3)

        self.set_output(self.REGULATED, raw)

    #
    # Sensor reads
    #

    def get_power(self):
        '''
        Returns watts.
        '''

        data = self.send_command(bytes([0x02]), 4)

        raw = self.decode_u32(data)

        mw = raw / 100

        return mw / 1000

    def get_voltage(self):
        '''
        Returns volts.
        '''

        data = self.send_command(bytes([0x03]), 4)

        raw = self.decode_u32(data)

        return raw / 100

    def get_ds18b20_temperature(self):
        '''
        Returns C.
        '''

        data = self.send_command(bytes([0x04]), 4)

        raw = self.decode_u32(data)

        return raw / 100 - 255.5

    def get_sht40_temperature(self):
        '''
        Returns C.
        '''

        data = self.send_command(bytes([0x05]), 4)

        raw = self.decode_u32(data)

        return raw / 100 - 254

    def get_sht40_humidity(self):
        '''
        Returns %RH.
        '''

        data = self.send_command(bytes([0x06]), 4)

        raw = self.decode_u32(data)

        return raw / 100 - 254

    def get_current(self):
        '''
        Returns amps.
        '''

        data = self.send_command(bytes([0x07]), 4)

        raw = self.decode_u32(data)

        ma = raw / 100

        return ma / 1000

    #
    # Status
    #

    def get_status(self):
        '''
        Returns dictionary with all output states.
        '''

        data = self.send_command(bytes([0x08]), 10)

        return {
            "dc": [bool(x) for x in data[0:5]],

            "usb": [bool(x) for x in data[5:7]],

            "regulated_voltage":
                data[7] * 15.3 / 255,

            "pwm":
                [
                    data[8] * 100 / 255,
                    data[9] * 100 / 255,
                ],
        }

    #
    # Power cycle
    #

    def power_cycle(self):
        '''
        Execute power cycle sequence.
        '''

        self.send_command(bytes([0xFF, 0xFF]), 2)

        time.sleep(1)

        self.send_command(bytes([0xFE, 0xFE]), 2)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:\npython svbony_powerbox.py dc1-5/dc_all on/off/status (port)\npython svbony_powerbox.py usb1-2/usb_all on/off/status (port)\n")
        sys.exit(1)
        
    if not os.path.isfile('port.txt'): 
        f=open('port.txt','w')
        f.write('\n')
        f.close()

        
    channel = sys.argv[1]
    action = sys.argv[2]
    
    f=open('port.txt','r')
    port=f.readlines()[0].strip()
    f.close()
    
    port = sys.argv[3] if len(sys.argv) > 3 else port
    
    f=open('port.txt','w')
    f.write(port+'\n')
    f.close()
        
    if (not action in ['on','off','status']) or (not channel in ['dc1','dc2','dc3','dc4','dc5','dc_all','usb1','usb2','usb_all']) or not port:
        print("Usage:\npython svbony_powerbox.py dc1-5/dc_all on/off/status (port)\npython svbony_powerbox.py usb1-2/usb_all on/off/status (port)\n")
        sys.exit(1) 
        
    try:
        box = SVBonyPowerBox(port)
        
        if action=='status': status=box.get_status()
        if 'dc' in channel:
            if '_' in channel:                
                for i in range(5):
                    if action=='on': box.set_dc(i, True)
                    elif action=='off': box.set_dc(i, False)
                    elif action=='status': print(f'DC{i}: {"on" if status["dc"][i] else "off"}')   
            else:
                i=int(channel[2])
                if action=='on': box.set_dc(i, True)
                elif action=='off': box.set_dc(i, False)
                elif action=='status': print(f'DC{i}: {"on" if status["dc"][i] else "off"}')  
        
        if 'usb' in channel:
            if '_' in channel:                
                for i in range(2):
                    if action=='on': box.set_usb(i, True)
                    elif action=='off': box.set_usb(i, False)
                    elif action=='status': print(f'USB{i}: {"on" if status["usb"][i] else "off"}')   
            else:
                i=int(channel[3])
                if action=='on': box.set_usb(i, True)
                elif action=='off': box.set_usb(i, False)
                elif action=='status': print(f'DC{i}: {"on" if status["usb"][i] else "off"}')  
        
        
        box.close()
        
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        print("Usage:\npython svbony_powerbox.py dc1-5/dc_all on/off/status (port)\npython svbony_powerbox.py usb1-2/usb_all on/off/status (port)\n")
        sys.exit(1) 
