import _thread

import machine
import utime
from machine import ADC, PWM, Pin


class Led:
    def __init__(self, pin, freq=5000, on_duty=256):
        self.pin = PWM(Pin(pin, Pin.OUT), freq=freq, duty_u16=0)
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
        self.time_sv = 0

        self.pin.irq(handler=self.button_event, trigger=trigger)


class GenericADCReader:
    def __init__(self, pin, min_value=0, max_value=100):
        if min_value >= max_value:
            raise Exception("Min value is greater or equal to max value")

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
        self.power_pin.on()

        self.max_value = 100
        self.min_value = 0

    def read(self):
        v = super().read()

        return v

    # Il valore dell'umidità del terreno è letta con tensione inversa al grado di umidità
    def value(self):
        return self.max_value - super().value()


class EchoDistance:
    SOUND_SPEED = 0.0343

    def __init__(self, trigger_pin, echo_pin):
        self.trigger = Pin(trigger_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)

        self.echo_timeout_us = 500 * 2 * 30

    def measure(self):
        """
        Restituisce la distanza misurata dal sensore (in cm).
        Questa funzione non riporta buoni risultati se chiamata troppo velocemente (circa 1s di tempo?)
        """

        self.trigger.value(0)  # Stabilize the sensor
        utime.sleep_us(5)
        self.trigger.value(1)
        # Send a 10us pulse.
        utime.sleep_us(10)
        self.trigger.value(0)
        try:
            pulse_time = machine.time_pulse_us(self.echo, 1, self.echo_timeout_us)
            return (pulse_time * EchoDistance.SOUND_SPEED) / 2
        except OSError as ex:
            if ex.args[0] == 110:  # 110 = ETIMEDOUT, troppo tempo per leggere
                print("Echo time out")
                return 0
            raise ex


class WaterPump:
    def __init__(self, relay):
        self.relay = Pin(relay, Pin.OUT)
        self._off()

    # Il segnale di enable funziona al contrario.
    # La pompa è spenta per segnali alti sul pin.
    def _on(self):
        self.relay.off()

    def _off(self):
        self.relay.on()

    def _toggle(self):
        self.relay.value(not self.relay.value())

    def activate(self):
        self._on()
        utime.sleep(2)
        self._off()


class Buzzer:
    def _init_buzzer(self):
        self._buzzer = PWM(
            Pin(self._buzzer_pin), freq=1000, duty_u16=0
        )  # spento all'avvio

    def __init__(self, buzzer_pin):
        self._buzzer_pin = buzzer_pin
        self._init_buzzer()
        self._lock = _thread.allocate_lock()
        self._must_stop = False
        self._is_playing = False

        # --- NOTE ---
        self.NOTE_C5 = 523
        self.NOTE_D5 = 587
        self.NOTE_E5 = 659
        self.NOTE_F5 = 698
        self.NOTE_G5 = 784
        self.NOTE_B5 = 988
        self.NOTE_A5 = 880
        self.NOTE_FS5 = 740  # F#
        self.NOTE_AS5 = 932  # A#

        self.NOTE_B4 = 494
        self.NOTE_G4 = 392
        self.NOTE_A4 = 440

        self.NOTE_D6 = 1175
        self.NOTE_C6 = 1047
        self.NOTE_E6 = 1319

        # --- MELODIA JINGLE BELLS ---
        self._melody1 = [
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_G5,
            self.NOTE_C5,
            self.NOTE_D5,
            self.NOTE_E5,
            self.NOTE_F5,
            self.NOTE_F5,
            self.NOTE_F5,
            self.NOTE_F5,
            self.NOTE_F5,
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_D5,
            self.NOTE_D5,
            self.NOTE_E5,
            self.NOTE_D5,
            self.NOTE_G5,
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_G5,
            self.NOTE_C5,
            self.NOTE_D5,
            self.NOTE_E5,
            self.NOTE_F5,
            self.NOTE_F5,
            self.NOTE_F5,
            self.NOTE_F5,
            self.NOTE_F5,
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_G5,
            self.NOTE_G5,
            self.NOTE_F5,
            self.NOTE_D5,
            self.NOTE_C5,
        ]

        self._durations1 = [
            8,
            8,
            4,
            8,
            8,
            4,
            8,
            8,
            8,
            8,
            2,
            8,
            8,
            8,
            8,
            8,
            8,
            8,
            16,
            16,
            8,
            8,
            8,
            8,
            4,
            4,
            8,
            8,
            4,
            8,
            8,
            4,
            8,
            8,
            8,
            8,
            2,
            8,
            8,
            8,
            8,
            8,
            8,
            8,
            16,
            8,
            8,
            8,
            8,
            8,
            4,
        ]

        # --- MELODIA WE WISH YOU A MERRY CHRISTMAS ---
        self._melody2 = [
            self.NOTE_D5,
            self.NOTE_G5,
            self.NOTE_G5,
            self.NOTE_A5,
            self.NOTE_G5,
            self.NOTE_FS5,
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_E5,
            self.NOTE_A5,
            self.NOTE_A5,
            self.NOTE_B5,
            self.NOTE_A5,
            self.NOTE_G5,
            self.NOTE_FS5,
            self.NOTE_D5,
            self.NOTE_D5,
            self.NOTE_B5,
            self.NOTE_B5,
            self.NOTE_C6,
            self.NOTE_B5,
            self.NOTE_A5,
            self.NOTE_G5,
            self.NOTE_E5,
            self.NOTE_D5,
            self.NOTE_E5,
            self.NOTE_A5,
            self.NOTE_FS5,
            self.NOTE_G5,
        ]

        self._durations2 = [
            4,
            4,
            8,
            8,
            8,
            8,
            4,
            4,
            4,
            4,
            8,
            8,
            8,
            8,
            4,
            4,
            4,
            4,
            8,
            8,
            8,
            8,
            4,
            4,
            4,
            4,
            4,
            4,
            2,
        ]

        # --- MELODIA LET IT SNOW ---
        self._melody3 = [
            self.NOTE_C5,
            self.NOTE_C5,
            self.NOTE_C6,
            self.NOTE_C6,
            self.NOTE_AS5,
            self.NOTE_A5,
            self.NOTE_G5,
            self.NOTE_F5,
            self.NOTE_C5,
            self.NOTE_C5,
            self.NOTE_C5,
            self.NOTE_G5,
            self.NOTE_F5,
            self.NOTE_G5,
            self.NOTE_F5,
            self.NOTE_E5,
            self.NOTE_C5,
            self.NOTE_D5,
            self.NOTE_D6,
            self.NOTE_D6,
            self.NOTE_C6,
            self.NOTE_AS5,
            self.NOTE_A5,
            self.NOTE_G5,
            self.NOTE_E6,
            self.NOTE_D6,
            self.NOTE_C6,
            self.NOTE_C6,
            self.NOTE_AS5,
            self.NOTE_A5,
            self.NOTE_A5,
            self.NOTE_G5,
            self.NOTE_F5,
        ]

        self._durations3 = [
            8,
            8,
            8,
            8,
            4,
            4,
            8,
            4,
            2,
            8,
            8,
            4,
            4,
            4,
            8,
            4,
            2,
            4,
            8,
            8,
            4,
            4,
            8,
            2,
            4,
            16,
            4,
            4,
            16,
            4,
            4,
            16,
            2,
        ]

    def _play_thread(self, melody, durations):
        for i in range(len(melody)):
            self._lock.acquire()

            if self._must_stop:
                self._stop()
                self._lock.release()
                return

            note = melody[i]
            duration = int(1000 / durations[i])

            self._buzzer.freq(note)
            self._buzzer.duty(700)

            self._lock.release()

            utime.sleep_ms(duration)
            self._buzzer.duty(0)
            utime.sleep_ms(int(duration * 0.6))

        self._lock.acquire()
        self._stop()
        self._lock.release()

    def _play(self, melody, durations):
        self._lock.acquire()

        if self._is_playing:
            print("Tried to play music while already playing.")
            self._lock.release()
            return

        self._init_buzzer()
        self._is_playing = True
        _thread.start_new_thread(self._play_thread, (melody, durations))

        self._lock.release()

    def play_jb(self):
        self._play(self._melody1, self._durations1)

    def play_wwmc(self):
        self._play(self._melody2, self._durations2)

    def play_lis(self):
        self._play(self._melody3, self._durations3)

    def _stop(self):
        self._buzzer.duty(0)
        self._buzzer.deinit()
        self._is_playing = False
        self._must_stop = False

    def stop(self):
        self._lock.acquire()

        self._must_stop = True

        self._lock.release()
