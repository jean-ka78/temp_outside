
from lib.threading import _thread

from link import Lin
conn = Lin()

from lib.umqtt.simple import MQTTClient
mqtt_host = "greenhouse.net.ua"
mqtt_username = "test"  # Your Adafruit IO username
mqtt_password = "qwerty"  # Adafruit IO Key
mqtt_publish_topic = "pico_out"  # The MQTT topic for your Adafruit IO Feed
mqtt_receive_topic = "home/#"  # The MQTT topic for your Adafruit IO Feed
mqtt_client_id = "pico_w"

class Clien:
    def __init__(self):
        self.values = {}
        # self.connect = Lin()
        # self.connect.start()
        self.mqtt = MQTTClient(
                client_id=mqtt_client_id,
                server=mqtt_host,
                user=mqtt_username,
                password=mqtt_password)
        if conn.wlan.isconnected() == True:
            self.mqtt.set_callback(self.mqtt_subscription_callback)
            self.mqtt.connect()
            self.mqtt.subscribe(mqtt_receive_topic)
        # else:
        #     conn.start()
        # Before connecting, tell the MQTT client to use the callback
        # self.mqtt.set_callback(self.mqtt_subscription_callback)
        # self.mqtt.connect()
        # Once connected, subscribe to the MQTT topic
        # self.mqtt.subscribe(mqtt_receive_topic)
        print("Connected and subscribed")

    def start(self):
        _thread.start_new_thread(self.mqtt_update, ())
            
    def mqtt_update(self):
        try:
            while True:
                self.mqtt.wait_msg()
        except Exception as e:
            print(f'Failed to wait for MQTT messages: {e}')
        finally:
            self.mqtt.disconnect()
            
    def mqtt_subscription_callback(self, topic, message):
        # print (f'Topic {topic} received message {message}')  # Debug print out of what was received over MQTT
        topic_str = topic.decode('utf-8')
        self.values[topic_str] = message.decode('utf-8')

