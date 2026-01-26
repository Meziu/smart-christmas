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

        self.display.clear()
        self.display.draw_header()
        # self.display.draw_stats_page()
        # self.display.draw_music_page()
        self.display.set_page(self.display.PAGE_STATS)

        self.sensors.tree_lights.on()
        # self.sensors._buzzer.play_jb()
        # self.sensors.buzzer.play_wwmc()
        # self.sensors.buzzer.play_lis()

        while True:
            self.display.update_page()

            # self.display.draw_stats_data(data)
            # self.display.draw_music_update()

            self.display.oled.show()
