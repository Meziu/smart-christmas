import utime

from displaymanager import DisplayManager
from mqttmanager import MQTTManager
from sensormanager import SensorManager


class SmartChristmas:
    def __init__(self):
        self.sensors = SensorManager()
        self.sensors.red_led_strip.on()
        self.sensors.blue_led_strip.on()
        self.display = DisplayManager(self.sensors)
        self.mqtt = MQTTManager(
            self.display, self.sensors
        )  # Il display è passato per mostrare le informazioni di collegamento

    def run(self):
        self.display.show_logo()

        utime.sleep(2)

        self.sensors.red_led_strip.off()
        self.sensors.blue_led_strip.off()

        self.display.clear()
        self.display.draw_header()
        # self.display.draw_stats_page()
        # self.display.draw_music_page()
        self.display.set_page(0)

        i = 0
        j = 0

        while True:
            i += 1
            if i % 3 == 0:
                j += 1
                self.display.set_page(j % 2)

            self.sensors.read_sensors()
            self.mqtt.upload_sensor_data(self.sensors.sensor_data)
            print(self.sensors.sensor_data)

            self.display.update_page()

            # self.display.draw_stats_data(self.sensors.sensor_data)
            # self.display.draw_music_update()

            self.display.oled.show()
