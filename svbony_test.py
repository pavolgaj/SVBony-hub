from pprint import pprint
from svbony_powerbox import SVBonyPowerBox

box = SVBonyPowerBox("/dev/ttyUSB0")

try:
    if not box.handshake():
        print("Device not responding")
        exit(1)

    print("Input voltage:", box.get_voltage(), "V")
    print("Current:", box.get_current(), "A")
    print("Power:", box.get_power(), "W")

    print("DS18B20:", box.get_ds18b20_temperature(), "°C")
    print("SHT40:", box.get_sht40_temperature(), "°C")
    print("Humidity:", box.get_sht40_humidity(), "%")

    pprint(box.get_status())

    # Turn DC1 on
    box.set_dc(1, True)

    # Set PWM heater 1 to 50%
    box.set_pwm(1, 50)

    # Set regulated output to 12V
    box.set_regulated_voltage(12.0)

finally:
    box.close()
    