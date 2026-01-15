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

        self.display.clear()
        self.display.draw_header()
       # self.display.draw_stats_page()
        self.display.draw_music_page()

        while True:
            self.sensors.read_sensors()
            print(self.sensors.sensor_data)

            self.display.draw_header_data()
            #self.display.draw_stats_data(self.sensors.sensor_data)

            self.display.oled.show()
