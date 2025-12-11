from sensors import Button, DirtMoisture, EchoDistance, LDR, WaterPump
from dht import DHT22
from utime import sleep

#Max velocità dell'EchoDistance: 2 secondi

class SensorManager():
    MOISTURE_LOW_LEVEL = 20 # umidità del terreno troppo bassa sotto al 20%
    EMPTY_TANK_LEVEL = 10 # serbatoio considerato vuoto sotto al 10%
    
    def __init__():
        self.echo = EchoDistance(pin_digitalout, pin_digitalin)
        self.dirtmoisture = DirtMoisture(pin_adc, pin_digitalout)
        self.dht = DHT22(Pin(pin_digitalinout))
        self.pump = WaterPump(pin_digitalout)
        self.ldr = LDR(pin_adc)
        self.reset_button = Button(pin_digitalin)
        
        self.sensor_data = {}
        
        # schermo oled: pin_digitalout, pin_digitalout
        
    def tank_level():
        MIN_DISTANCE = 4 # 4cm è il limite inferiore di lettura del sensore a ultrasuoni (serbatoio pieno)
        MAX_DISTANCE = 15 # 15cm è l'altezza del serbatoio (serbatoio vuoto)
        distance = self.echo.measure()
        
        percentage = (MAX_DISTANCE - distance) / (MAX_DISTANCE - MIN_DISTANCE) * 100
        
        return percentage
        
    def read_sensors():
        # Max velocità del DHT22: 2 secondi
        # Il sensore di umidità del terreno attende comunque un secondo internamente
        self.dht.measure()
        
        self.sensor_data["air_temperature"] = self.dht.temperature()
        self.sensor_data["air_humidity"] = self.dht.humidity()
        self.sensor_data["soil_moisture"] = self.dirtmoisture.value()
        self.sensor_data["light_level"] = self.ldr.value()
        self.sensor_data["tank_level"] = self.tank_level()
        
        sleep(2)
        
    def should_activate_pump():
        # Il serbatoio ha abbastanza acqua da pompare e l'umidità del terreno è sotto un determinato livello
        return self.sensor_data["tank_level"] > EMPTY_TANK_LEVEL and self.sensor_data["soil_moisture"] < MOISTURE_LOW_LEVEL
