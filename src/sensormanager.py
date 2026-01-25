import _thread

import machine
import utime
from dht import DHT22
from machine import DAC, PWM, Pin
from utime import sleep

from sensors import LDR, Button, Buzzer, DirtMoisture, EchoDistance, Led, WaterPump

# Max velocità dell'EchoDistance: 2 secondi


class SensorManager:
    EMPTY_TANK_LEVEL = 10  # serbatoio considerato vuoto sotto al 10%

    def __init__(self):
        self._lock = _thread.allocate_lock()

        self._echo = EchoDistance(5, 18)
        self._dirtmoisture = DirtMoisture(34, 17)
        self._dht = DHT22(Pin(23))
        self._pump = WaterPump(33)
        self._ldr = LDR(35)
        self._buzzer = Buzzer(14)

        self.red_led_strip = Pin(25, Pin.OUT)
        self.blue_led_strip = Pin(26, Pin.OUT)
        self.red_led_strip.on()
        self.blue_led_strip.on()

        self.tree_lights = Led(19, on_duty=512)
        self.tree_lights.off()

        self._must_activate_pump = False
        self._moisture_low_level = 30  # umidità del terreno troppo bassa sotto al 30%

        def press(b):
            machine.reset()

        self._reset_button = Button(12, press)

        self._sensor_data = {}

        _thread.start_new_thread(self._sensor_thread, ())

    def _tank_level(self):
        MIN_DISTANCE = 4  # 4cm è il limite inferiore di lettura del sensore a ultrasuoni (serbatoio pieno)
        MAX_DISTANCE = 17  # 15cm è l'altezza del serbatoio (serbatoio vuoto)
        distance = self._echo.measure()

        percentage = (MAX_DISTANCE - distance) / (MAX_DISTANCE - MIN_DISTANCE) * 100

        return percentage

    def _read_sensors(self):
        # Max velocità del DHT22: 2 secondi
        # Il sensore di umidità del terreno attende comunque un secondo internamente
        self._dht.measure()

        self._sensor_data["air_temperature"] = round(self._dht.temperature(), 1)
        self._sensor_data["air_humidity"] = round(self._dht.humidity(), 1)
        self._sensor_data["soil_moisture"] = round(self._dirtmoisture.value(), 1)
        self._sensor_data["light_level"] = round(self._ldr.value(), 1)
        self._sensor_data["tank_level"] = round(self._tank_level(), 1)

    def get_sensor_data(self):
        self._lock.acquire()

        d = self._sensor_data.copy()

        self._lock.release()

        return d

    def activate_pump(self):
        self._lock.acquire()

        try:
            self._must_activate_pump = True
        finally:
            self._lock.release()

    def set_moisture_low_level(self, level):
        self._lock.acquire()

        try:
            self._moisture_low_level = level
        finally:
            self._lock.release()

    def _should_activate_pump(self):
        if self._must_activate_pump:
            self._must_activate_pump = False  # Consuma il comando
            return True

        # Il serbatoio ha abbastanza acqua da pompare e l'umidità del terreno è sotto un determinato livello
        return (
            # self.sensor_data["tank_level"] > self.EMPTY_TANK_LEVEL and
            self._sensor_data["soil_moisture"] < self._moisture_low_level
            or self._must_activate_pump
        )

    def _sensor_thread(self):
        self._dirtmoisture.power_pin.on()
        utime.sleep(0.3)
        while True:
            self._lock.acquire()

            self._read_sensors()

            # Quando il livello di umidità del terreno scende sotto il threshold
            if self._should_activate_pump():
                print("Pump activated")
                self._pump.activate()

            self._lock.release()

            self._dirtmoisture.power_pin.off()
            utime.sleep(2)
            self._dirtmoisture.power_pin.on()
            utime.sleep(2)
