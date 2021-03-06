from time import sleep

import ubinascii
import urequests
from machine import Pin, reset


def start():
    while True:
        try:
            mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode().replace(':','')
            req = urequests.get('https://nugget.galletta.xyz/motd?mac=' + mac)
            data = req.json()
            req.close()
            for message in data['message-list']:
                lprint(message, data['delay'])
        # Need to change this once specific error is known        
        except Exception as e:
            print(e)
            lprint('Unexpected errorRebooting...', 3)
            reset()

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
        from machine import I2C

        from nodemcu_gpio_lcd import I2cLcd

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
