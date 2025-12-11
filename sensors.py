from machine import Pin, PWM, ADC
import utime

class Led:
    def __init__(self,pin, freq=5000, on_duty=256):
        self.pin = PWM(Pin(pin, Pin.OUT),freq=freq,duty_u16=0)
        self.on_duty = on_duty
        
    def duty(self, duty):
        self.pin.duty(duty)
        
    def on(self):
        self.duty(self.on_duty)
        
    def off(self):
        self.duty(0)
        
    def toggle(self):
        if self.pin.duty() > 0:
            self.off()
        else:
            self.on()
        
class Button:
    def button_event(self, b):
        curr = utime.ticks_ms()
        delay = utime.ticks_diff(curr, self.time_sv)
    
        if delay < self.bounce:
            return
    
        self.time_sv = curr
    
        self.f(b)
    
        
    def __init__(self, pin, f, bounce=200, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        self.f = f
        self.bounce = bounce
        self.time_sv=0
        
        self.pin.irq(handler=self.button_event, trigger=trigger)
    

class GenericADCReader:
    """light dependent resistor (LDR)"""

    def __init__(self, pin, min_value=0, max_value=100):
        if min_value >= max_value:
            raise Exception('Min value is greater or equal to max value')

        # initialize ADC (analog to digital conversion)
        # create an object ADC
        self.adc = ADC(Pin(pin, Pin.IN))
        self.min_value = min_value
        self.max_value = max_value

    def read(self):
        return self.adc.read()

    def value(self):
        return (self.max_value - self.min_value) * self.read() / 4095

class LDR(GenericADCReader):
    pass
    
class DirtMoisture(GenericADCReader):
    def __init__(self, pin, power_pin):
        super().__init__(pin)
        
        self.power_pin = Pin(power_pin, Pin.OUT)
        self.power_pin.off()
    
    def read(self):
        self.power_pin().on()
        time.sleep(0.8)
        v = super().read()
        self.power_pin().off()
        
        return v
    
class ServoMotor:
    """Servo Motor"""

    duty_min = 26
    duty_max = 128
    def __init__(self, pin, motor_calibration=-13):
        self.pin = PWM(Pin(pin, Pin.OUT), freq=50)
        self.motor_calibration = motor_calibration

    def set_angle(self, angle):
        """Set rotation angle between 0-180"""
        
        angle = angle + self.motor_calibration
        self.pin.duty(int(self.duty_min + (angle/180)*(self.duty_max-self.duty_min)))
        
class StepMotor:
    stepper_pins = []
    
    # Definisco i pin per stepper motor
    def __init__(self, pin1,pin2,pin3,pin4):
        self.stepper_pins.append(Pin(pin1, Pin.OUT))
        self.stepper_pins.append(Pin(pin2, Pin.OUT))
        self.stepper_pins.append(Pin(pin3, Pin.OUT))
        self.stepper_pins.append(Pin(pin4, Pin.OUT))


    # full-step con 2 bobbine attive per ogni step
    # due bobbine accese per ogni step -> più coppia
    #il valore (0=spento, 1=acceso) da dare a quel pin nel passo corrente.
    step_sequence = [
        [1, 0, 0, 1], 
        [1, 1, 0, 0], 
        [0, 1, 1, 0], 
        [0, 0, 1, 1], 
    ]

    #la half-step corrispondente (8 stati) è questa:
    # Half-step (mezzo passo): alterna 1 bobina e 2 bobine
    # Ordine pin: [IN1, IN2, IN3, IN4]
    step_sequence_half = [
        [1,0,0,0],  # solo IN1
        [1,0,0,1],  # IN1+IN4
        [0,0,0,1],  # solo IN4
        [0,0,1,1],  # IN3+IN4
        [0,0,1,0],  # solo IN3
        [0,1,1,0],  # IN2+IN3
        [0,1,0,0],  # solo IN2
        [1,1,0,0],  # IN1+IN2
    ]

    #direction = +1 (antiorario), -1 (orario)
    #steps = numero di passi da eseguire
    #delay = tempo tra un passo e l'altro
    #step_index tiene traccia della posizione corrente nella sequenza di attivazione (fase) del motore.

    def step(self, direction, steps, delay):
        step_index=0
        for i in range(steps):
            # l'operatore % garantisce che step_index rimanga all'interno dell'intervallo valido (in questo caso [0-3]),
            # assicurando che la sequenza dei passi venga ripetuta ciclicamente.
            # indica la riga quindi quale passo
            step_index = (step_index + direction) % len(self.step_sequence) # se la sequenza ha 4 stati è come fare mod 4
            
            #pin_index determina la colonna (quindi la bobbina)
            for pin_index in range(len(self.stepper_pins)):
                #Esempio: se step_index = 2, la sequenza è [0, 1, 1, 0]
                # Se pin_index = 0 → pin_value = 0
                # Se pin_index = 1 → pin_value = 1
                # Se pin_index = 2 → pin_value = 1
                # Se pin_index = 3 → pin_value = 0
                pin_value = self.step_sequence[step_index][pin_index]
                #Scrive il valore sul pin fisico, accendendo o spegnendo la bobina
                self.stepper_pins[pin_index].value(pin_value)
            
            #Aspetta il tempo delay prima di passare al prossimo passo.
            #Pausa più corta → motore più veloce. Pausa più lunga → motore più lento.
            utime.sleep(delay)
            
class EchoDistance():
    SOUND_SPEED = 0.0343
    
    def __init__(self, trigger_pin, echo_pin):
        self.trigger = Pin(trigger_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        
    def measure(self):
        """
        Restituisce la distanza misurata dal sensore (in cm).
        Questa funzione non riporta buoni risultati se chiamata troppo velocemente (circa 1s di tempo?)
        """
        self.trigger.off()
        utime.sleep_us(2)
        self.trigger.on()
        utime.sleep_us(10)
        self.trigger.off()
        
        while self.echo.value() == 0:
            inizio = utime.ticks_us()
        
        while self.echo.value() == 1:
            fine = utime.ticks_us()
            
        durata = utime.ticks_diff(fine, inizio)
        
        return (durata * EchoDistance.SOUND_SPEED) / 2

class WaterPump:
    def __init__(self, relay):
        self.relay = Pin(relay, Pin.OUT)
        self.off()
    
    # Il segnale di enable funziona al contrario.
    # La pompa è spenta per segnali alti sul pin.
    def on():
        self.relay.off()
    def off():
        self.relay.on()
    def toggle():
        relay.value(not relay.value())
