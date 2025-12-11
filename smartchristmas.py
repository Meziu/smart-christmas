from gibrary.managers import DisplayManager, MQTTManager, SensorManager

class SmartChristmas():
    def __init__(self):
        self.display = DisplayManager()
        self.mqtt = MQTTManager()
        self.sensors = SensorManager()
        
    def run(self):
        pass
