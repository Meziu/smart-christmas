import machine
import utime
from dht import DHT22
from machine import DAC, PWM, Pin
from utime import sleep

from sensors import LDR, Button, Buzzer, DirtMoisture, EchoDistance, Led, WaterPump

# Max velocità dell'EchoDistance: 2 secondi


class SensorManager:
    MOISTURE_LOW_LEVEL = 20  # umidità del terreno troppo bassa sotto al 20%
    EMPTY_TANK_LEVEL = 10  # serbatoio considerato vuoto sotto al 10%

    def __init__(self):
        self.echo = EchoDistance(5, 18)
        self.dirtmoisture = DirtMoisture(34, 17)
        self.dht = DHT22(Pin(23))
        self.pump = WaterPump(33)
        self.ldr = LDR(35)
        self.buzzer = Buzzer(14)

        self.red_led_strip = Pin(25, Pin.OUT)
        self.blue_led_strip = Pin(26, Pin.OUT)

        def press(b):
            machine.reset()

        self.reset_button = Button(12, press)

        self.sensor_data = {}

    def tank_level(self):
        MIN_DISTANCE = 4  # 4cm è il limite inferiore di lettura del sensore a ultrasuoni (serbatoio pieno)
        MAX_DISTANCE = 17  # 15cm è l'altezza del serbatoio (serbatoio vuoto)
        distance = self.echo.measure()

        percentage = (MAX_DISTANCE - distance) / (MAX_DISTANCE - MIN_DISTANCE) * 100

        return percentage

    def read_sensors(self):
        # Max velocità del DHT22: 2 secondi
        # Il sensore di umidità del terreno attende comunque un secondo internamente
        self.dht.measure()

        self.sensor_data["air_temperature"] = round(self.dht.temperature(), 1)
        self.sensor_data["air_humidity"] = round(self.dht.humidity(), 1)
        self.sensor_data["soil_moisture"] = round(self.dirtmoisture.value(), 1)
        self.sensor_data["light_level"] = round(self.ldr.value(), 1)
        self.sensor_data["tank_level"] = round(self.tank_level(), 1)

        sleep(2)

    def should_activate_pump(self):
        # Il serbatoio ha abbastanza acqua da pompare e l'umidità del terreno è sotto un determinato livello
        return (
            self.sensor_data["tank_level"] > self.EMPTY_TANK_LEVEL
            and self.sensor_data["soil_moisture"] < self.MOISTURE_LOW_LEVEL
        )
