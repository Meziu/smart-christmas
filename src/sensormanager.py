import _thread

import machine
import utime
from dht import DHT22
from machine import DAC, PWM, Pin
from utime import sleep

from sensors import LDR, Button, Buzzer, DirtMoisture, EchoDistance, Led, WaterPump

# Max velocità dell'EchoDistance: 2 secondi


class SensorManager:
    must_activate_pump = False
    moisture_low_level = 30  # umidità del terreno troppo bassa sotto al 30%
    EMPTY_TANK_LEVEL = 10  # serbatoio considerato vuoto sotto al 10%

    def __init__(self):
        self._lock = _thread.allocate_lock()

        self.echo = EchoDistance(5, 18)
        self.dirtmoisture = DirtMoisture(34, 17)
        self.dht = DHT22(Pin(23))
        self.pump = WaterPump(33)
        self.ldr = LDR(35)
        self.buzzer = Buzzer(14)

        self.red_led_strip = Pin(25, Pin.OUT)
        self.blue_led_strip = Pin(26, Pin.OUT)
        self.red_led_strip.on()
        self.blue_led_strip.on()

        self.tree_lights = Led(19, on_duty=512)
        self.tree_lights.off()

        def press(b):
            machine.reset()

        self.reset_button = Button(12, press)

        self._sensor_data = {}

    def _tank_level(self):
        MIN_DISTANCE = 4  # 4cm è il limite inferiore di lettura del sensore a ultrasuoni (serbatoio pieno)
        MAX_DISTANCE = 17  # 15cm è l'altezza del serbatoio (serbatoio vuoto)
        distance = self.echo.measure()

        percentage = (MAX_DISTANCE - distance) / (MAX_DISTANCE - MIN_DISTANCE) * 100

        return percentage

    def read_sensors(self):
        self._lock.acquire_lock()

        try:
            # Max velocità del DHT22: 2 secondi
            # Il sensore di umidità del terreno attende comunque un secondo internamente
            self.dht.measure()

            self._sensor_data["air_temperature"] = round(self.dht.temperature(), 1)
            self._sensor_data["air_humidity"] = round(self.dht.humidity(), 1)
            self._sensor_data["soil_moisture"] = round(self.dirtmoisture.value(), 1)
            self._sensor_data["light_level"] = round(self.ldr.value(), 1)
            self._sensor_data["tank_level"] = round(self._tank_level(), 1)
        finally:
            self._lock.release_lock()

        sleep(2)

    def get_sensor_data(self):
        self._lock.acquire_lock()

        try:
            return self._sensor_data.copy()
        finally:
            self._lock.acquire_lock()

    def _should_activate_pump(self):
        if self.must_activate_pump:
            self.must_activate_pump = False  # Consuma il comando
            return True

        # Il serbatoio ha abbastanza acqua da pompare e l'umidità del terreno è sotto un determinato livello
        return (
            # self.sensor_data["tank_level"] > self.EMPTY_TANK_LEVEL and
            self._sensor_data["soil_moisture"] < self.moisture_low_level
            or self.must_activate_pump
        )

    def _sensor_thread(self):
        while True:
            self._lock.acquire_lock()

            try:
                self.read_sensors()
            finally:
                self._lock.acquire_lock()

            utime.sleep(2)
