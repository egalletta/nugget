def run():
    import urequests
    from time import sleep
    while True:
        req = urequests.get('http://n-u-g-g-e-t.herokuapp.com/motd')
        print(req.text)
        sleep(5)

if __name__ == '__main__':
    run()