from sensormanager import SensorManager
from displaymanager import DisplayManager
from mqttmanager import MQTTManager
import utime

class SmartChristmas():
    def __init__(self):
        self.display = DisplayManager()
        self.mqtt = MQTTManager(self.display.oled)
        self.sensors = SensorManager()

    def run(self):
        self.display.show_logo()

sc = SmartChristmas()

utime.sleep(1)

sc.display.oled.fill(0)
sc.display.show_logo()

utime.sleep(2)

sc.display.oled.fill(0)
sc.display.show_stats()

while True:
    print(sc.sensors.read_sensors())
