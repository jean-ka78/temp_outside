import network
from time import sleep
from machine import Pin
from lib.threading import _thread
# from mqtt import Clien
ssid = 'aonline'
passw = '1qaz2wsx3edc'
class Lin:
    def __init__(self):
        self.led = Pin('LED', Pin.OUT)
        self.wlan = network.WLAN(network.STA_IF)

        self.connect()

        self.j = 0
        print(self.wlan.ifconfig())
        if self.wlan.isconnected() == True:
            self.led.value(True)
        else:
            self.led.value(False)
    
    def connect(self, max_attempt=3):
        try:
            self.init_connection()
        except:
            self.j = +1
            if self.j < max_attempt:
                print('disconnect')
                self.wlan.disconnect()
                self.wlan.active(False)
                self.connect()
            else:
                return

    def init_connection(self, timeout=10):
        self.i=0
        while True:
            print('Waiting for connection...')
            self.wlan.active(True)
            self.wlan.connect(ssid,passw)
            if self.wlan.isconnected() == True:
                break
            else:
                self.i += 1
            if self.i > timeout:
                print('i', str(self.i))
                raise Exception('Connection timeout')
            sleep(5)

if __name__ == '__main__':
    Lin()
# Lin()



