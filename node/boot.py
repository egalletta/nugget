import network
import urequests

def main():
    do_connect()
    response = urequests.get('https://raw.githubusercontent.com/egalletta/nugget/master/node/payload.py')
    f = open('payload.py', 'w')
    f.write(response.text)
    f.close()
    run()

def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('BlueberryNet', 'RedSox1$')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

def run():
    import payload
    payload.run()

main()