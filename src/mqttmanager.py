import _thread

import network
import ntptime
import ssd1306
import ujson
import utime
from machine import I2C, Pin
from umqtt.simple import MQTTClient

from utils import localtime_italy_str


class MQTTManager:
    WIFI_SSID = "iPhone di Cili"
    WIFI_PASSWORD = "bongos34"

    CLIENT_ID = "SCT1"
    BROKER = "test.mosquitto.org"
    USER = None
    PASSWORD = None

    MACRO_TOPIC = "unisa/diem/iot/smartchristmas/"
    SENSOR_TOPIC = MACRO_TOPIC + "env"
    COMMAND_TOPIC = MACRO_TOPIC + "cmd"

    def subCallback(self, topic, msg):
        print("Received message: ", topic, msg)

    def update_thread(self):
        while True:
            try:
                self.client.wait_msg()
            except OSError:
                print("MQTT connection lost, reconnecting...")
                try:
                    self.client.disconnect()
                except:
                    pass
                utime.sleep(2)
                reconnect()

    def __init__(self, display, sensors):
        sta_if = network.WLAN(network.STA_IF)

        sta_if.active(True)
        sta_if.disconnect()

        sta_if.connect(self.WIFI_SSID, self.WIFI_PASSWORD)

        display.show_connecting()  # Connecting to Wifi

        while not sta_if.isconnected():
            print(".", end="")
            utime.sleep(0.1)

        print(" Connesso al Wi-Fi!")

        display.show_connected()  # Connesso!

        # Sincronizzazione orologio
        try:
            ntptime.settime()
            print("Ora sincronizzata via NTP")
        except:
            print("Errore sincronizzazione NTP")

        self.client = MQTTClient(
            self.CLIENT_ID,
            self.BROKER,
            user=self.USER,
            password=self.PASSWORD,
            port=1883,
            keepalive=30,
            ssl=False,
        )
        self.client.set_callback(self.subCallback)
        self.client.connect()
        self.client.subscribe(self.COMMAND_TOPIC + "/lights")

        # Lancia un thread per leggere immediatamente i messaggi MQTT
        _thread.start_new_thread(self.update_thread, ())

        print("MQTT connected!")

    def upload_sensor_data(self, data):
        data["timestamp"] = localtime_italy_str()

        message = ujson.dumps(data)
        self.client.publish(self.SENSOR_TOPIC, message)
