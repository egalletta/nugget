import urequests
from time import sleep
from boot import lprint

def start():
    while True:
        req = urequests.get('http://n-u-g-g-e-t.herokuapp.com/motd')
        lprint(req.text)
        sleep(5)

if __name__ == '__main__':
    run()