import network
import machine
import math
import time
from umqtt.simple import MQTTClient

# Константи
WIFI_TIMEOUT = 10  # Секунди для тайм-ауту Wi-Fi
SLEEP_INTERVAL = 1  # Секунди між вимірюваннями
CORRECTION_OFFSET = -5 - 2.0  # Поправка для температури

adc_count = 100
raw = [0] * adc_count

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

    def connect_wifi(self):
        if not self.wifi_connected:
            print("Connecting to Wi-Fi...")
            self.wlan.active(True)
            self.wlan.connect(self.ssid, self.password)
            start_time = time.time()
            while not self.wlan.isconnected():
                if time.time() - start_time > WIFI_TIMEOUT:
                    print("Failed to connect to Wi-Fi")
                    return
            print("Connected to Wi-Fi")
            self.wifi_connected = True

    def connect_mqtt(self):
        if not self.mqtt_connected:
            print("Connecting to MQTT...")
            try:
                self.mqtt.connect()
                print("Connected to MQTT")
                self.mqtt_connected = True
            except Exception as e:
                print(f"Failed to connect to MQTT: {e}")

    def read_ntc_sensor(self):
        Vin = 3.3
        Ro = 10000  # 10k резистор
        adc_resolution = 65535
        A = 0.001129148
        B = 0.000234125
        C = 0.0000000876741

        for i in range(len(raw)):
            adc_value = self.adc.read_u16()
            raw[i] = adc_value

        raw.sort()
        sum_list = sum(raw)
        middle = sum_list / len(raw)

        Vout = (middle * Vin) / adc_resolution
        if Vout <= 0:
            print("Error: Vout is zero or negative, skipping this measurement.")
            return self.Temp_C  # Повертаємо останнє коректне значення

        Rt = (Vin * Ro / Vout) - Ro
        TempK = 1 / (A + (B * math.log(Rt)) + C * math.pow(math.log(Rt), 3))
        TempC = TempK - 273.15
        TempC = TempC + CORRECTION_OFFSET

        self.Temp_C = 0.9 * self.Temp_C + 0.1 * TempC 

        return round(self.Temp_C, 2)

    def publish_temperature(self, temperature):
        if self.mqtt_connected:
            try:
                self.mqtt.publish(self.mqtt_topic, str(temperature))
            except Exception as e:
                print(f"Failed to publish temperature: {e}")
                self.mqtt_connected = False  # Mark MQTT as disconnected

    def run(self):
        while True:
            if not self.wifi_connected:
                self.connect_wifi()
            if self.wifi_connected and not self.mqtt_connected:
                self.connect_mqtt()

            # Перевірка на втрату підключення
            if self.wifi_connected and not self.wlan.isconnected():
                print("Wi-Fi connection lost. Reconnecting...")
                self.wifi_connected = False

            if self.mqtt_connected:
                try:
                    self.mqtt.ping()
                except Exception as e:
                    print(f"MQTT connection lost: {e}")
                    self.mqtt_connected = False

            # Читання і публікація температури
            temperature = self.read_ntc_sensor()
            print('Temp = ', temperature, '`C')
            self.publish_temperature(temperature)

            time.sleep(SLEEP_INTERVAL)  # Пауза між вимірюваннями

# Приклад використання
if __name__ == "__main__":
    ssid = "aonline"
    password = "1qaz2wsx3edc"
    mqtt_server = "greenhouse.net.ua"
    mqtt_port = 1883
    mqtt_topic = "home/pico/current_temperature"
    mqtt_user = "test"
    mqtt_u_pass = "qwerty"
    analog_pin = 26

    ntc_w = NTCWithWiFi(ssid, password, mqtt_server, mqtt_port, mqtt_topic, mqtt_user, mqtt_u_pass, analog_pin)
    ntc_w.run()
