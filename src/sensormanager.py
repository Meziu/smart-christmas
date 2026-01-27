import _thread

import machine
import utime
from dht import DHT22
from machine import Pin

from sensors import LDR, Button, Buzzer, DirtMoisture, EchoDistance, Led, WaterPump


class SensorManager:
    def __init__(self):
        self._lock = _thread.allocate_lock()

        self._echo = EchoDistance(5, 18)
        self._dirtmoisture = DirtMoisture(34, 17)
        self._pump = WaterPump(33)
        self._ldr = LDR(35)

        self._init_buzzer()

        # A volte il DHT ha timeout al collegamento.
        # Nel caso non ci si riesca a collegare, si ritenta l'avvio.
        try:
            self._dht = DHT22(Pin(23))
        except OSError as _:
            machine.reset()

        self._green_led_strip = Pin(25, Pin.OUT)
        self._blue_led_strip = Pin(26, Pin.OUT)
        self._green_led_strip.on()
        self._blue_led_strip.on()

        self.tree_lights = Led(19, on_duty=512)
        self.tree_lights.off()

        self._is_playing = False
        self._data_available = False
        self._must_activate_pump = False
        self._moisture_low_level = 30  # umidità del terreno troppo bassa sotto al 30%

        def press(b):
            print("Reset button")
            machine.reset()

        self._reset_button = Button(12, press)

        self._sensor_data = {}

        self._sensor_data["air_temperature"] = 0
        self._sensor_data["air_humidity"] = 0
        self._sensor_data["soil_moisture"] = 0
        self._sensor_data["light_level"] = 0
        self._sensor_data["tank_level"] = 0

        _thread.start_new_thread(self._sensor_thread, ())

    def _tank_level(self):
        MIN_DISTANCE = 4  # 4cm è il limite inferiore di lettura del sensore a ultrasuoni (serbatoio pieno)
        MAX_DISTANCE = 16  # 16 cm è l'altezza del serbatoio (serbatoio vuoto)
        distance = self._echo.measure()

        percentage = (MAX_DISTANCE - distance) / (MAX_DISTANCE - MIN_DISTANCE) * 100

        return percentage

    def _read_sensors(self):
        try:
            # Max velocità del DHT22: 2 secondi
            # Il sensore di umidità del terreno attende comunque un secondo internamente
            self._dht.measure()
        except OSError as e:
            print("Errore con DHT:", e)
            utime.sleep(2)
            self._dht = DHT22(Pin(23))
            return

        self._sensor_data["air_temperature"] = round(self._dht.temperature(), 1)
        self._sensor_data["air_humidity"] = round(self._dht.humidity(), 1)
        self._sensor_data["soil_moisture"] = round(self._dirtmoisture.value(), 1)
        self._sensor_data["light_level"] = round(self._ldr.value(), 1)
        self._sensor_data["tank_level"] = round(self._tank_level(), 1)

        self._data_available = True

    def led_ok(self):
        self._green_led_strip.off()
        self._blue_led_strip.off()

    def get_sensor_data(self):
        self._lock.acquire()

        d = self._sensor_data.copy()

        self._lock.release()

        return d

    def get_new_sensor_data(self):
        self._lock.acquire()

        # Si ritorna un valore solo se i dati non
        # sono mai stati ottenuti tramite questa funzione.
        # Utile per il sistema MQTT.
        if not self._data_available:
            self._lock.release()
            return None

        self._data_available = False

        d = self._sensor_data.copy()

        self._lock.release()

        return d

    def activate_pump(self):
        self._lock.acquire()

        self._must_activate_pump = True

        self._lock.release()

    def set_moisture_low_level(self, level):
        self._lock.acquire()

        self._moisture_low_level = level

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
        utime.sleep(2)
        while True:
            self._lock.acquire()

            self._read_sensors()

            # Quando il livello di umidità del terreno scende sotto il threshold
            if self._should_activate_pump():
                print("Pump activated")
                self._pump.activate()

            self._lock.release()

            # Spegniamo il dirt moisture sensor per
            # prevenire corrosione dei sensori.
            self._dirtmoisture.power_pin.off()
            utime.sleep(4)

            # Lasciamo il dirt moisture acceso per un secondo
            # per avere una lettura stabile.
            self._dirtmoisture.power_pin.on()
            utime.sleep(1)

    def _init_buzzer(self):
        self._buzzer = Buzzer(14)

        self._music = [
            self._buzzer.play_jb,
            self._buzzer.play_wwmc,
            self._buzzer.play_lis,
        ]

    # Restituisce True se la riproduzione è iniziata con successo,
    # False altrimenti.
    def play_music(self, idx):
        self._lock.acquire()

        if self._buzzer._is_playing:
            self._lock.release()
            return False

        self._music[idx]()

        self._lock.release()

        return True

    def stop_music(self):
        self._lock.acquire()

        self._buzzer.stop()

        self._lock.release()

    def is_playing_music(self):
        self._lock.acquire()

        f = self._buzzer._is_playing

        self._lock.release()

        return f
