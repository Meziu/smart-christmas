from umqtt.robust import MQTTClient
import ujson
import network
from machine import Pin, I2C
import ssd1306
import utime
import ntptime

class MQTTManager():
    WIFI_SSID = "iPhone di Cili"
    WIFI_PASSWORD = "bongos34"

    CLIENT_ID = "SCT1"
    BROKER    = "broker.emqx.io"
    USER      = None
    PASSWORD  = None

    MACRO_TOPIC = "unisa/diem/iot/smartchristmas/"
    SENSOR_TOPIC = MACRO_TOPIC + "env"
    ACTUATOR_TOPIC = MACRO_TOPIC + "act"

    def subCallback(self, topic, msg):
        print(topic,msg)

    def __init__(self, display):
        sta_if = network.WLAN(network.STA_IF)

        sta_if.active(True)
        sta_if.disconnect()

        sta_if.connect(self.WIFI_SSID, self.WIFI_PASSWORD)

        display.show_connecting() # Connecting to Wifi

        while not sta_if.isconnected():
            print(".", end="")
            utime.sleep(0.1)

        print(" Connesso al Wi-Fi!")

        display.show_connected() # Connesso!

        # Sincronizzazione orologio
        try:
            ntptime.settime()
            print("Ora sincronizzata via NTP")
        except:
            print("Errore sincronizzazione NTP")

        self.client = MQTTClient(self.CLIENT_ID, self.BROKER, user=self.USER, password=self.PASSWORD, port=1883, keepalive=30, ssl=False)
        self.client.set_callback(self.subCallback)
        self.client.connect()
        self.client.subscribe(self.ACTUATOR_TOPIC)

        print("MQTT connected!")

    def upload_sensor_data(self, data):
        message = ujson.dumps(data)
        self.client.publish(self.SENSOR_TOPIC, message)

# Test di funzionamento
#if __name__ == "__main__":
#    i2c = I2C(0, scl=Pin(22), sda=Pin(21))
#
#    oled_width = 128
#    oled_height = 64
#    oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
#    man = MQTTManager(oled)
#
#    man.upload_sensor_data({"sto": "chillando"})
