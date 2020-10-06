import urequests
from time import sleep
from machine import Pin
import ubinascii

def start():
    while True:
        mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode().replace(':','')
        req = urequests.get('http://nugget.galletta.xyz/motd?mac=' + mac).json()
        for message in req['message-list']:
            lprint(message, req['delay'])

def lprint(text: str, delay: float):
    try:
        from nodemcu_gpio_lcd import GpioLcd
        lcd = GpioLcd(rs_pin=Pin(16),
                    enable_pin=Pin(5),
                    d4_pin=Pin(4),
                    d5_pin=Pin(0),
                    d6_pin=Pin(2),
                    d7_pin=Pin(14),
                    num_lines=2, num_columns=16)
    except (ImportError, OSError):
        from nodemcu_gpio_lcd import I2cLcd
        from machine import I2C
        # The PCF8574 has a jumper selectable address: 0x20 - 0x27
        DEFAULT_I2C_ADDR = 0x27
        i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
        lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)
    if len(text) <= 32:
        print(text)
        lcd.clear()
        sleep(0.15)
        lcd.putstr(text)
        sleep(delay)
    else:
        to_display = text[:32]
        print(to_display)
        lcd.clear()
        sleep(0.15)
        lcd.putstr(to_display)
        sleep(delay)
        lprint(text[32:], delay)

start()