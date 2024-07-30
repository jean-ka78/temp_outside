import network
import time

def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.active(True)
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
        print("Connected to Wi-Fi")
    return wlan

def ensure_wifi_connection(wlan, ssid, password):
    while not wlan.isconnected():
        print("Wi-Fi disconnected. Reconnecting...")
        wlan = connect_to_wifi(ssid, password)
        time.sleep(5)

# Configure your Wi-Fi credentials
wifi_ssid = "aonline"
wifi_password = "1qaz2wsx3edc"

# Connect to Wi-Fi
wlan = connect_to_wifi(wifi_ssid, wifi_password)

while True:
    ensure_wifi_connection(wlan, wifi_ssid, wifi_password)
    # Your main code here
