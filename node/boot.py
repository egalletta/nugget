import network
from nodemcu_gpio_lcd import GpioLcd
import urequests
from time import sleep
from machine import Pin

def main():
    lprint('nuggetBOOTv1.0.0Connecting...')
    do_connect()
    lprint('nuggetBOOTv1.0.0Connected!')
    sleep(1)
    lprint('nuggetBOOTv1.0.0Downloading OS..')
    response = urequests.get('https://raw.githubusercontent.com/egalletta/nugget/master/node/main.py')
    f = open('payload.py', 'w')
    f.write(response.text)
    f.close()
    lprint('nuggetBOOTv1.0.0Running..')

def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        f = open('wifi_pw')
        pw = f.read()
        f.close()
        sta_if.connect('BlueberryNet', pw)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

def lprint(s):
    lcd = GpioLcd(rs_pin=Pin(16),
                  enable_pin=Pin(5),
                  d4_pin=Pin(4),
                  d5_pin=Pin(0),
                  d6_pin=Pin(2),
                  d7_pin=Pin(14),
                  num_lines=2, num_columns=16)
    print(s)
    lcd.clear()
    sleep(0.15)
    lcd.putstr(s)

main()