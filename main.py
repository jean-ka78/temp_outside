import network
import machine
import math
import time
from umqtt.simple import MQTTClient

# Константи
WIFI_TIMEOUT = 20
SLEEP_INTERVAL = 10000  # мс
CORRECTION_OFFSET = 0.0
adc_count = 20

class NTCWithWiFi:
    def __init__(self, ssid, password, mqtt_server, mqtt_port, mqtt_topic, mqtt_user, mqtt_u_pass, analog_pin):
        self.ssid = ssid
        self.password = password
        self.mqtt_server = mqtt_server
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
        self.mqtt_u_pass = mqtt_u_pass
        self.mqtt_topic = mqtt_topic
        self.analog_pin = analog_pin
        self.wlan = network.WLAN(network.STA_IF)
        self.mqtt = MQTTClient('pico', self.mqtt_server, self.mqtt_port, self.mqtt_user, self.mqtt_u_pass)
        self.adc = machine.ADC(self.analog_pin)
        self.wifi_connected = False
        self.mqtt_connected = False
        self.Temp_C = 0.0
        self.timer = machine.Timer()

    def connect_wifi(self):
        if not self.wifi_connected:
            print("Connecting to Wi-Fi...")
            self.wlan.active(True)
            self.wlan.connect(self.ssid, self.password)
            start_time = time.time()
            while not self.wlan.isconnected():
                if time.time() - start_time > WIFI_TIMEOUT:
                    print("Wi-Fi connection timeout.")
                    return
            print("Connected to Wi-Fi.")
            self.wifi_connected = True

    def connect_mqtt(self):
        if not self.mqtt_connected:
            print("Connecting to MQTT...")
            try:
                self.mqtt.connect()
                print("Connected to MQTT.")
                self.mqtt_connected = True
            except Exception as e:
                print(f"MQTT connection failed: {e}")

    def read_ntc_sensor(self):
        Vin = 3.3
        Ro = 11350
        adc_resolution = 65535
        A = 0.001129148
        B = 0.000234125
        C = 0.0000000876741

        total = 0
        for _ in range(adc_count):
            total += self.adc.read_u16()
        average = total / adc_count

        Vout = (average * Vin) / adc_resolution
        if Vout <= 0:
            print("Invalid Vout.")
            return self.Temp_C

        Rt = (Vin * Ro / Vout) - Ro
        logRt = math.log(Rt)
        TempK = 1 / (A + B * logRt + C * logRt**3)
        TempC = TempK - 273.15 + CORRECTION_OFFSET
        self.Temp_C = 0.9 * self.Temp_C + 0.1 * TempC

        return round(self.Temp_C, 2)

    def publish_temperature(self, temperature):
        if self.mqtt_connected:
            try:
                self.mqtt.publish(self.mqtt_topic, str(temperature))
            except Exception as e:
                print(f"Publish failed: {e}")
                self.mqtt_connected = False

    def measure_and_publish(self, timer):
        # Wi-Fi перевірка
        if not self.wifi_connected:
            self.connect_wifi()
        if self.wifi_connected and not self.wlan.isconnected():
            print("Wi-Fi disconnected.")
            self.wifi_connected = False

        # MQTT повторне підключення
        if self.wifi_connected and not self.mqtt_connected:
            self.connect_mqtt()

        temperature = self.read_ntc_sensor()
        print('Temp =', temperature, 'C')
        self.publish_temperature(temperature)

    def run(self):
        print("Starting periodic measurement every", SLEEP_INTERVAL // 1000, "seconds.")
        self.timer.init(period=SLEEP_INTERVAL, mode=machine.Timer.PERIODIC, callback=self.measure_and_publish)

# Приклад використання
if __name__ == "__main__":
    ssid = "aonline"
    password = "1qaz2wsx3edc"
    mqtt_server = "greenhouse.net.ua"
    mqtt_port = 1883
    mqtt_topic = "home/pico/current_temperature"
    mqtt_user = "mqtt"
    mqtt_u_pass = "qwerty"
    analog_pin = 26

    ntc = NTCWithWiFi(ssid, password, mqtt_server, mqtt_port, mqtt_topic, mqtt_user, mqtt_u_pass, analog_pin)
    ntc.run()

    while True:
        time.sleep(1)
