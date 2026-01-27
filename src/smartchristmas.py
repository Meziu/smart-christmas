import utime

from displaymanager import DisplayManager
from mqttmanager import MQTTManager
from sensormanager import SensorManager


class SmartChristmas:
    def __init__(self):
        self.sensors = SensorManager()
        self.display = DisplayManager(self.sensors)
        self.mqtt = MQTTManager(
            self.display, self.sensors
        )  # Il display è passato per mostrare le informazioni di collegamento

    def run(self):
        self.display.show_logo()

        utime.sleep(2)

        self.sensors.led_ok()

        self.display.clear()
        self.display.draw_header()
        self.display.set_page(self.display.PAGE_STATS)

        self.sensors.tree_lights.on()

        while True:
            self.display.update_page()

            self.display.oled.show()
