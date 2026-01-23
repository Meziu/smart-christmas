import utime

from displaymanager import DisplayManager
from mqttmanager import MQTTManager
from sensormanager import SensorManager


class SmartChristmas:
    def __init__(self):
        self.sensors = SensorManager()
        self.display = DisplayManager(self.sensors)
        self.mqtt = MQTTManager(
            self.display
        )  # Il display è passato per mostrare le informazioni di collegamento

    def run(self):
        self.display.show_logo()

        utime.sleep(1)

        self.display.clear()
        self.display.draw_header()
        # self.display.draw_stats_page()
        # self.display.draw_music_page()
        self.display.next_page()

        i = 0

        while True:
            i += 1
            if i % 5 == 0:
                self.display.next_page()

            self.sensors.read_sensors()
            self.mqtt.upload_sensor_data(self.sensors.sensor_data)
            print(self.sensors.sensor_data)
            self.mqtt.client.check_msg()

            self.display.update_page()

            # self.display.draw_stats_data(self.sensors.sensor_data)
            # self.display.draw_music_update()

            self.display.oled.show()
