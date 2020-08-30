from machine import Pin
from utime import sleep, ticks_ms
from nodemcu_gpio_lcd import GpioLcd
import urequests
from time import sleep
from boot import lprint

def run():
    while True:
        req = urequests.get('http://n-u-g-g-e-t.herokuapp.com/motd')
        lprint(req.text)
        sleep(5

if __name__ == '__main__':
    run()