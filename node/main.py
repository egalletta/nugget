from nodemcu_gpio_lcd import GpioLcd
import urequests
from time import sleep
from machine import Pin
import ubinascii

def start():
    while True:
        data = {
            'mac': ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
        }
        req = urequests.get('http://n-u-g-g-e-t.herokuapp.com/motd', json=data).json()
        for message in req['message-list']:
            lprint(message, 5)

def lprint(text: str, delay: float):
    lcd = GpioLcd(rs_pin=Pin(16),
                  enable_pin=Pin(5),
                  d4_pin=Pin(4),
                  d5_pin=Pin(0),
                  d6_pin=Pin(2),
                  d7_pin=Pin(14),
                  num_lines=2, num_columns=16)
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