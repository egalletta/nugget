from machine import Pin
from utime import sleep, ticks_ms
from nodemcu_gpio_lcd import GpioLcd
import urequests
from time import sleep

lcd = GpioLcd(rs_pin=Pin(16),
                  enable_pin=Pin(5),
                  d4_pin=Pin(4),
                  d5_pin=Pin(0),
                  d6_pin=Pin(2),
                  d7_pin=Pin(14),
                  num_lines=2, num_columns=16)

def run():
    while True:
        req = urequests.get('http://n-u-g-g-e-t.herokuapp.com/motd')
        lprint(req.text)
        sleep(5)

def lprint(s):
    print(s)
    lcd.clear()
    sleep(0.15)
    lcd.putstr(s)

if __name__ == '__main__':
    run()