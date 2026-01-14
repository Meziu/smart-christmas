from sensormanager import SensorManager
from displaymanager import DisplayManager
from mqttmanager import MQTTManager
import utime

class SmartChristmas():
    def __init__(self):
        self.sensors = SensorManager()
        self.display = DisplayManager()
        self.mqtt = MQTTManager(self.display) # Il display è passato per mostrare le informazioni di collegamento

    def run(self):
        self.display.show_logo()
        utime.sleep(1)

        self.display.show_blank()
        self.display.show_logo()

        utime.sleep(2)

        self.display.show_blank()
        self.display.show_stats_page()

        while True:
            print(self.sensors.read_sensors())
