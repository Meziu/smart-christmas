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

    MACRO_TOPIC = b"unisa/diem/iot/smartchristmas"
    SENSOR_TOPIC = MACRO_TOPIC + b"/env"
    COMMAND_TOPIC = MACRO_TOPIC + b"/cmd"

    LIGHTS_TOPIC = COMMAND_TOPIC + b"/lights"
    WATERINGLEVEL_TOPIC = COMMAND_TOPIC + b"/wateringlevel"
    PUMP_TOPIC = COMMAND_TOPIC + b"/pump"
    MUSIC_TOPIC = COMMAND_TOPIC + b"/music"

    def sub_callback(self, topic, msg):
        print("Received message: ", topic, msg)
        self.cmd_actions[topic](msg)

    def lights_callback(self, msg):
        if msg == b"on":
            self.sensors.tree_lights.on()
        elif msg == b"off":
            self.sensors.tree_lights.off()

    def wateringlevel_callback(self, msg):
        try:
            v = int(msg)
            self.sensors.moisture_low_level = v
        except (ValueError, TypeError):
            return

    def pumpactivation_callback(self, msg):
        if msg == b"act":
            self.sensors.must_activate_pump = True

    def music_callback(self, msg):
        try:
            v = int(msg)
            if v < 0 or v > 2:
                raise ValueError()
            self.display.setup_music(v)
            self.display.set_page(1)
        except (ValueError, TypeError):
            return

    def update_thread(self):
        while True:
            try:
                self.client.wait_msg()
            except OSError as e:
                print("Errore nell'attesa di un messaggio MQTT:", e)
                self.client.disconnect()
                self.client.connect()

    def __init__(self, display, sensors):
        self.cmd_actions = {
            self.LIGHTS_TOPIC: self.lights_callback,
            self.WATERINGLEVEL_TOPIC: self.wateringlevel_callback,
            self.PUMP_TOPIC: self.pumpactivation_callback,
            self.MUSIC_TOPIC: self.music_callback,
        }

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

        self.sensors = sensors
        self.display = display

        self.client = MQTTClient(
            self.CLIENT_ID,
            self.BROKER,
            user=self.USER,
            password=self.PASSWORD,
            port=1883,
            keepalive=30,
            ssl=False,
        )
        self.client.set_callback(self.sub_callback)
        self.client.connect()
        self.client.subscribe(self.LIGHTS_TOPIC)
        self.client.subscribe(self.WATERINGLEVEL_TOPIC)
        self.client.subscribe(self.PUMP_TOPIC)
        self.client.subscribe(self.MUSIC_TOPIC)

        # Lancia un thread per leggere immediatamente i messaggi MQTT
        _thread.start_new_thread(self.update_thread, ())

        print("MQTT connected!")

    def upload_sensor_data(self, data):
        data["timestamp"] = localtime_italy_str()

        message = ujson.dumps(data)
        self.client.publish(self.SENSOR_TOPIC, message)
