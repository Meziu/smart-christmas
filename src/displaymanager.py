import random

import framebuf
import network
import ssd1306
import utime
from machine import I2C, Pin

from utils import localtime_italy, music, text_width


class DisplayManager:
    OLED_WIDTH = 128
    OLED_HEIGHT = 64

    PAGE_STATS = 0
    PAGE_MUSIC = 1

    AIR_HUMIDITY_LABEL = "Umid.:"
    DIRT_MOISTURE_LABEL = "Terra:"
    TANK_LABEL = "Acqua"
    TEMPERATURE_LABEL = "Temp.:"

    AIR_HUMIDITY_LABEL_WIDTH = text_width(AIR_HUMIDITY_LABEL)
    DIRT_MOISTURE_LABEL_WIDTH = text_width(DIRT_MOISTURE_LABEL)
    TEMPERATURE_LABEL_WIDTH = text_width(TEMPERATURE_LABEL)

    # Dimensione delle stringhe scritte nello scorso rendering della
    # pagina di statistiche così da permettere un clear localizzato della superficie oled
    _hum_width = 0
    _moist_width = 0
    _temp_width = 0
    _song_name = ""

    # Inizializziamo gli offset casuali per lo spettrogramma
    _offsets = [random.randint(3, 8) for _ in range(9)]
    _play_step = 0

    def __init__(self, sensor_manager):
        # ESP32 Pin assignment to OLED
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21))

        self.oled = ssd1306.SSD1306_I2C(self.OLED_WIDTH, self.OLED_HEIGHT, self.i2c)

        # binding del gestore di sensori
        self._sensor_manager = sensor_manager

        # formato: funzione di setup del layout di pagina, funzione di update
        self._pages = [
            (self.draw_stats_page, self.draw_stats_data),
            (self.draw_music_page, self.draw_music_update),
        ]

    def clear(self):
        self.oled.fill(0)

    def clear_page(self):
        self.oled.rect(0, 16, 128, 64, 0, True)

    def show_connecting(self):
        self.clear()
        self.oled.text("Connessione", 24, 24, 1)
        self.oled.text("al WiFi", 24, 34, 1)
        self.oled.show()

    def show_connected(self):
        self.clear()
        self.oled.text("Connesso!!!", 24, 24, 1)
        self.oled.show()

    # Svolto solo al boot, non pre-allochiamo
    def show_logo(self):
        self.clear()
        albero_bits = bytearray(
            b"\x00\x00\x03\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x0c\xc0\x00\x00\x00\x00\x0c\xc0\x00\x00\x00\x0000\x00\x00\x00\x0000\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x03\x00\x03\x00\x00\x00\x03\x00\x0b\x00\x00\x00\x0c\x00 \xc0\x00\x00\x0d\x00\x80\xc0\x00\x000$\x000\x00\x000\x00\x000\x00\x00<\x00\x00\xf0\x00\x00<\x00\x00\xf0\x00\x00\x03\xc0\x0f\x00\x00\x00\x03\xc0\x0f\x00\x00\x00\x0f\x00\x03\xc0\x00\x00\x0f\x00\x03\xc0\x00\x00\xf0\x00\x00<\x00\x00\xf4\x00\x00<\x00\x03\x01\x00\x00C\x00\x03\x00 \x02\x03\x00\x0c\x00\x02 \x00\xc0\x0c\x00\x00\x00\x00\xc0\x0f\xc0\x00\x00\x0f\xc0\x0f\xc0\x00\x00\x0f\xc0\x00<\x00\x00\xf0\x00\x00<\x00\x00\xf0\x00\x00\xf0\x00\x00<\x00\x00\xf0\x00\x00<\x00\x0f\x00\x00\x00C\xc0\x0f\x00\x00\x01\x03\xc00@\x00\x08\x0000\x08\x00@\x000\xc0\x00\x84\x00\x00\x0c\xc0\x00\x00\x00\x00\x0c\xfc\x00\x00\x00\x00\xfc\xfc\x00\x00\x00\x00\xfc\x03\xff\xc0\x0f\xff\x00\x03\xff\xc0\x0f\xff\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xff\xfc\x00\x00\x00\x00\xff\xfc\x00\x00"
        )
        stella_bits = bytearray(
            b"\x06\x00\x09\x00\x09\x00p\xe0\x80\x10\x89\x10@  @F I 0\xc0"
        )
        lettera_c_bits = bytearray(
            b"\x0f\xf8\x00\x10\x06\x00 \x01\x00@\x00\x80\x80\x00@\x80\xc0@\x81 @\x81 @\x81 @\x81 @\x81 @\x81 @\x81 @\x81 @\x81?\xc0\x81\x00\x00\x81\x00\x00\x81\x00\x00\x81\x00\x00\x81?\xc0\x81 @\x81 @\x81 @\x81 @\x81 @\x81 @\x81 @\x80\xc0@\x80\x00@@\x00\x80 \x01\x00\x10\x06\x00\x0f\xf8\x00"
        )
        lettera_s_bits = bytearray(
            b"\x07\xf8\x008\x07\x00 \x01\x00@\x00\x80@\x00\x80\x80`\x80\x80\x90\x80\x80\x90\x80\x80\x90\x80\x80\x90\x80\x80\x8f\x00\x80@\x00\x80 \x00@\x18\x00@\x06\x00 \x01\x00\x10\x00\x80\x0c\x00@\x02\x00@\x01\x00@\x00\x80@~@@\x81 @\x81 @\x81 @\x81 @\x81 @\x80\xc0@@\x00@@\x00@ \x00\x80\x18\x03\x00\x07\xfc\x00"
        )

        fb_albero = framebuf.FrameBuffer(albero_bits, 46, 50, framebuf.MONO_HLSB)
        self.oled.blit(fb_albero, 42, 11)

        fb_stella = framebuf.FrameBuffer(stella_bits, 12, 11, framebuf.MONO_HLSB)
        self.oled.blit(fb_stella, 59, 3)

        fb_lettera_c = framebuf.FrameBuffer(lettera_c_bits, 18, 33, framebuf.MONO_HLSB)
        self.oled.blit(fb_lettera_c, 100, 15)

        fb_lettera_s = framebuf.FrameBuffer(lettera_s_bits, 18, 33, framebuf.MONO_HLSB)
        self.oled.blit(fb_lettera_s, 10, 15)

        self.oled.show()

    # Layout delle componenti UI fisse in alto
    def draw_header(self):
        # Status Connettività WIFI
        self.oled.rect(109, 14, 3, 3, 1)
        self.oled.rect(113, 10, 3, 7, 1)
        self.oled.rect(117, 6, 3, 11, 1)
        self.oled.rect(121, 2, 3, 15, 1)

    def draw_wifi_strength(self):
        sta_if = network.WLAN(network.STA_IF)
        rssi = sta_if.status("rssi")

        tacche = [
            ((110, 15), (110, 15)),  # Tacca 1 (punto)
            ((114, 15), (114, 11)),  # Tacca 2
            ((118, 15), (118, 7)),  # Tacca 3
            ((122, 15), (122, 3)),  # Tacca 4
        ]

        # Determina quante tacche accendere
        if rssi > -50:
            tacche_attive = 4
        elif rssi > -60:
            tacche_attive = 3
        elif rssi > -70:
            tacche_attive = 2
        elif rssi > -80:
            tacche_attive = 1
        else:
            tacche_attive = 0

        # Disegna tutte le tacche: bianco se attiva, nero se inattiva
        for i, ((x1, y1), (x2, y2)) in enumerate(tacche):
            colore = 1 if i < tacche_attive else 0  # 1=bianco, 0=nero
            self.oled.line(x1, y1, x2, y2, colore)

    # Aggiornamento dinamico delle componenti UI fisse in alto
    def draw_header_data(self):
        # Orologio
        h, m = localtime_italy()[3:5]
        self.oled.rect(3, 8, 40, 8, 0, True)  # pulizia rect dell'orologio
        self.oled.text(f"{h:02d}:{m:02d}", 3, 8, 1)

        # Tacche del wifi
        self.draw_wifi_strength()

    def setup_music(self, music_idx):
        self._song_name = music[music_idx][0]
        self._song_length = music[music_idx][1]

    # Visualizza e prepara la prossima pagina
    def set_page(self, index):
        self.clear_page()

        # wrapping al termine delle pagine
        self._current_page = index

        # chiamata del setup della nuova pagina
        self._pages[self._current_page][0]()

        # Reset info
        self._play_step = 0

    def update_page(self):
        # update dell'header
        self.draw_header_data()

        # chiamata dell'update della pagina corrente
        self._pages[self._current_page][1]()

    # Layout e struttura della pagina informativa
    def draw_stats_page(self):
        testaBatteria_bits = bytearray(b"\x1f\x001\x80 \x80\xe0\xe0")

        self.oled.text(self.AIR_HUMIDITY_LABEL, 3, 20, 1)

        self.oled.text(self.DIRT_MOISTURE_LABEL, 3, 29, 1)

        self.oled.text(self.TANK_LABEL, 85, 53, 1)

        self.oled.text(self.TEMPERATURE_LABEL, 3, 43, 1)

        self.oled.line(109, 49, 109, 29, 1)

        self.oled.line(121, 49, 121, 29, 1)

        self.oled.line(110, 50, 120, 50, 1)

        fb_testaBatteria = framebuf.FrameBuffer(
            testaBatteria_bits, 11, 4, framebuf.MONO_HLSB
        )
        self.oled.blit(fb_testaBatteria, 110, 25)

    # Aggiorniamo solo le informazioni dinamiche sulla pagina e non tutto il layout
    # in modo tale da usare solo le risorse minime ed indispensabili per il rendering
    def draw_stats_data(self):
        pallinoGradi_bits = bytearray(b"@\xa0@")

        sensor_data = self._sensor_manager.sensor_data

        # Percentuale umidità dell'aria
        hum_str = f"{sensor_data['air_humidity']:.3g}%"
        self.oled.rect(
            3 + self.AIR_HUMIDITY_LABEL_WIDTH, 20, self._hum_width, 8, 0, True
        )  # pulizia del rect della stringa precedente
        self._hum_width = text_width(hum_str)
        self.oled.text(hum_str, 3 + self.AIR_HUMIDITY_LABEL_WIDTH, 20, 1)

        # Percentuale umidità del terreno
        moist_str = f"{sensor_data['soil_moisture']:.3g}%"
        self.oled.rect(
            3 + self.DIRT_MOISTURE_LABEL_WIDTH, 29, self._moist_width, 8, 0, True
        )  # pulizia del rect della stringa precedente
        self._moist_width = text_width(moist_str)
        self.oled.text(moist_str, 3 + self.DIRT_MOISTURE_LABEL_WIDTH, 29, 1)

        # Temperatura dell'aria
        temp_str = f"{sensor_data['air_temperature']:.1f}"
        self.oled.rect(
            3 + self.TEMPERATURE_LABEL_WIDTH, 41, self._temp_width + 3 + 8, 10, 0, True
        )  # pulizia del rect della stringa precedente
        self.moist_width = text_width(moist_str)
        self.oled.text(temp_str, 3 + self.TEMPERATURE_LABEL_WIDTH, 43, 1)
        self._temp_width = text_width(temp_str)

        fb_pallinoGradi = framebuf.FrameBuffer(
            pallinoGradi_bits, 3, 3, framebuf.MONO_HLSB
        )
        self.oled.blit(
            fb_pallinoGradi, 3 + self.TEMPERATURE_LABEL_WIDTH + self._temp_width, 41
        )
        self.oled.text(
            "C", 3 + self.TEMPERATURE_LABEL_WIDTH + self._temp_width + 3, 43, 1
        )  # il secondo + 3 proviene dalla dimensione del pallino per i gradi

        # Livello Serbatoio
        level = min(4, sensor_data["tank_level"] // 20)

        BAR_W = 9
        BAR_H = 4
        GAP = 1

        for i in range(4):
            by = 48 - i * (BAR_H + GAP)

            if i < level:
                # riempimento dal basso
                self.oled.rect(111, by - BAR_H + 1, BAR_W, BAR_H, 1, True)
            else:
                # pulizia
                self.oled.rect(111, by - BAR_H + 1, BAR_W, BAR_H, 0, True)

        utime.sleep(2)

    # Finto spettrogramma
    def draw_bars(self):
        self.oled.rect(47, 17, 79, 29, 0, True)  # pulizia sezione dello spettrogramma
        x_positions = [47, 51, 55, 59, 63, 67, 71, 75, 79]
        y_center = 29  # centro verticale
        for i, offset in enumerate(self._offsets):
            y_top = y_center - offset
            height = 2 * offset  # metà sopra e metà sotto il centro
            self.oled.rect(x_positions[i], y_top, 2, height, 1)

    # Layout pagina musicale
    def draw_music_page(self):
        # Info di riproduzione
        self.oled.text(self._song_name, 9, 46, 1)
        # linea lunga di riproduzione
        self.oled.line(7, 58, 119, 58, 1)
        # linee laterali delimitatrici
        self.oled.line(7, 57, 7, 59, 1)
        self.oled.line(120, 57, 120, 59, 1)

    def draw_music_update(self):
        MIN_O = 3
        MAX_O = 12

        for i in range(len(self._offsets)):
            # Scelta casuale di offset per il prossimo frame
            self._offsets[i] += random.choice([-2, -1, 0, 1, 2])

            # Ogni barra è influenzata anche dal valore dei suoi vicini
            if i == 0:
                self._offsets[i] = int(
                    (3 * self._offsets[i] + self._offsets[i + 1]) / 4
                )
            elif i == len(self._offsets) - 1:
                self._offsets[i] = int(
                    (3 * self._offsets[i] + self._offsets[i - 1]) / 4
                )
            else:
                self._offsets[i] = int(
                    (
                        3 * self._offsets[i]
                        + (self._offsets[i - 1] + self._offsets[i + 1]) / 2
                    )
                    / 4
                )

            # Esplosione di ampiezza casuale ogni tanto per diversificare
            if random.random() < 0.04:
                self._offsets[i] += random.randint(3, 6)

            # Clamp del valore ai limiti di spazio
            if self._offsets[i] < MIN_O:
                self._offsets[i] = MIN_O
            elif self._offsets[i] > MAX_O:
                self._offsets[i] = MAX_O

        self.draw_bars()

        # punto di riproduzione
        # self.oled.ellipse(10 + self._play_step, 58, 2, 2, 1, True)
        self.oled.line(8 + self._play_step, 56, 8 + self._play_step, 60, 1)

        if self._play_step:
            self._play_step = min(111, self._play_step + 1)

        utime.sleep(0.1)
