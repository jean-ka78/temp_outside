import network
import machine
import time
import ujson
from umqtt.simple import MQTTClient

class NTCWithWiFi:
    def __init__(self, ssid, password, mqtt_server, mqtt_topic, mqtt_user, mqtt_u_pass, analog_pin):
        self.ssid = ssid
        self.password = password
        self.mqtt_server = mqtt_server
        self.mqtt_user = mqtt_user
        self.mqtt_u_pass = mqtt_u_pass
        self.mqtt_topic = mqtt_topic
        self.analog_pin = analog_pin
        self.wlan = network.WLAN(network.STA_IF)
        self.mqtt = MQTTClient('pico', self.mqtt_server, self.mqtt_user, self.mqtt_u_pass)
        self.adc = machine.ADC(self.analog_pin)
        self.connected = False

    def connect_wifi(self):
        if not self.wlan.isconnected():
            print("Connecting to Wi-Fi...")
            self.wlan.active(True)
            self.wlan.connect(self.ssid, self.password)
            while not self.wlan.isconnected():
                pass
            print("Connected to Wi-Fi")
            self.connected = True

    def connect_mqtt(self):
        print("Connecting to MQTT...")
        self.mqtt.connect()
        print("Connected to MQTT")

    def read_ntc_sensor(self):
        raw_value = self.adc.read()
        return raw_value

    def publish_temperature(self, temperature):
        message = ujson.dumps({"temperature": temperature})
        self.mqtt.publish(self.mqtt_topic, message)

    def run(self):
        self.connect_wifi()
        self.connect_mqtt()

        while True:
            temperature = self.read_ntc_sensor()
            self.publish_temperature(temperature)
            time.sleep(60)  # Adjust the sleep interval as needed

# Example usage:
if __name__ == "__main__":
    ssid = "aonline"
    password = "1qaz2wsx3edc"
    mqtt_server = "greenhouse.net.ua"
    mqtt_topic = "home/current-temperature"
    mqtt_user = "test"
    mqtt_u_pass = "qwerty"
    analog_pin = 26

    ntc_w = NTCWithWiFi(ssid, password, mqtt_server, mqtt_topic, mqtt_user, mqtt_u_pass, analog_pin)
    ntc_w.run()
