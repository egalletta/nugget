import network
import urequests
from time import sleep
from machine import Pin
import ubinascii

def boot():
    do_connect()
    lprint('nuggetBOOTv1.0.0Connected!')
    sleep(1)
    lprint('nuggetBOOTv1.0.0Downloading OS..')
    response = urequests.get('https://raw.githubusercontent.com/egalletta/nugget/master/node/main.py')
    f = open('main.py', 'w')
    f.write(response.text)
    f.close()
    lprint('nuggetBOOTv1.0.0Running..')

def do_connect():
    lprint('nuggetBOOTv1.0.0Connecting...')
    sta_if = network.WLAN(network.STA_IF)
    mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode().replace(':','')
    lprint(mac + "    Connecting...")
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        f = open('wifi_ssid')
        ssid = f.read()
        f.close()
        f = open('wifi_pw')
        pw = f.read()
        f.close()
        sta_if.connect(ssid, pw)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

def lprint(s):
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
        from nodemcu_gpio_lcd import I2CLcd
        i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
        lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)
    print(s)
    lcd.clear()
    sleep(0.15)
    lcd.putstr(s)

boot() 