from sensormanager import SensorManager
from displaymanager import DisplayManager
from mqttmanager import MQTTManager

class SmartChristmas():
    def __init__(self):
        self.display = DisplayManager()
        self.mqtt = MQTTManager(self.display.oled)
        self.sensors = SensorManager()
        
    def run(self):
        self.display.show_logo()

SmartChristmas()

while True:
    pass
