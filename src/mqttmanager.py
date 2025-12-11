from umqtt.simple import MQTTClient
import ujson
import network
from machine import Pin, I2C
import ssd1306
import time

class MQTTManager():
    WIFI_SSID = "iPhone di Cili"
    WIFI_PASSWORD = "bongos34"

    CLIENT_ID = "SmartChristmasTree5"
    BROKER    = "test.mosquitto.org"
    USER      = ""
    PASSWORD  = ""
    
    MACRO_TOPIC = "unisa/diem/iot/smartchristmas/"
    SENSOR_TOPIC = MACRO_TOPIC + "env"
    ACTUATOR_TOPIC = MACRO_TOPIC + "act"
    
    def subCallback(self, topic,msg):
        print(topic,msg)
        if topic == ACTUATOR_TOPIC:
            if msg == b'1':
                led.on()
            elif msg == b'0':
                led.off()
    
    def __init__(self, oled):
        sta_if = network.WLAN(network.STA_IF)
        
        sta_if.active(True)
        sta_if.disconnect()
        
        sta_if.connect(self.WIFI_SSID, self.WIFI_PASSWORD)
        
        # ESP32 Pin assignment to OLED
        
        oled.fill(0)
        oled.text("Connecting", 24, 24, 1)
        oled.text("to WiFi", 24, 34, 1)
        oled.show()
        time.sleep(2)
        
        while not sta_if.isconnected():
            print(".", end="")
            time.sleep(0.1)
        
        print(" Connected!")
        
        oled.fill(0)
        oled.text("Connected!!!", 24, 24, 1)
        oled.show()
        time.sleep(1)
        
        self.client = MQTTClient(self.CLIENT_ID, self.BROKER, user=self.USER, password=self.PASSWORD)
        self.client.set_callback(self.subCallback)
        self.client.connect()
        self.client.subscribe(self.ACTUATOR_TOPIC)
    
    def upload_sensor_data(self, data):
        message = ujson.dumps(data)
        self.client.publish(self.SENSOR_TOPIC, message)
        
if __name__ == "__main__":
    i2c = I2C(0, scl=Pin(22), sda=Pin(21))

    oled_width = 128
    oled_height = 64
    oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
    man = MQTTManager(oled)
    
    man.upload_sensor_data({"sto": "chillando"})

