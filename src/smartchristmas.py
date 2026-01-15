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

        utime.sleep(2)

        self.display.clear()
        self.display.show_header()
        self.display.show_stats_page()

        while True:
            self.sensors.read_sensors()
            print(self.sensors.sensor_data)

            self.display.show_stats_data(self.sensors.sensor_data)
