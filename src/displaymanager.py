from machine import Pin, I2C
import ssd1306
import framebuf

# Helper per ottenere le dimensioni sullo schermo del testo.
def text_width(text):
    return len(text) * 8

class DisplayManager():
    OLED_WIDTH = 128
    OLED_HEIGHT = 64

    AIR_HUMIDITY_LABEL = "Umid.:"
    DIRT_MOISTURE_LABEL = "Terra:"
    TANK_LABEL = "Acqua"
    TEMPERATURE_LABEL = "Temp.:"

    AIR_HUMIDITY_LABEL_WIDTH = text_width(AIR_HUMIDITY_LABEL)
    DIRT_MOISTURE_LABEL_WIDTH = text_width(DIRT_MOISTURE_LABEL)
    TEMPERATURE_LABEL_WIDTH = text_width(TEMPERATURE_LABEL)

    def __init__(self):
        # ESP32 Pin assignment to OLED
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21))

        self.oled = ssd1306.SSD1306_I2C(self.OLED_WIDTH, self.OLED_HEIGHT, self.i2c)

    def clear(self):
        self.oled.fill(0)

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
        albero_bits = bytearray(b'\x00\x00\x03\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x0c\xc0\x00\x00\x00\x00\x0c\xc0\x00\x00\x00\x0000\x00\x00\x00\x0000\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x03\x00\x03\x00\x00\x00\x03\x00\x0b\x00\x00\x00\x0c\x00 \xc0\x00\x00\x0d\x00\x80\xc0\x00\x000$\x000\x00\x000\x00\x000\x00\x00<\x00\x00\xf0\x00\x00<\x00\x00\xf0\x00\x00\x03\xc0\x0f\x00\x00\x00\x03\xc0\x0f\x00\x00\x00\x0f\x00\x03\xc0\x00\x00\x0f\x00\x03\xc0\x00\x00\xf0\x00\x00<\x00\x00\xf4\x00\x00<\x00\x03\x01\x00\x00C\x00\x03\x00 \x02\x03\x00\x0c\x00\x02 \x00\xc0\x0c\x00\x00\x00\x00\xc0\x0f\xc0\x00\x00\x0f\xc0\x0f\xc0\x00\x00\x0f\xc0\x00<\x00\x00\xf0\x00\x00<\x00\x00\xf0\x00\x00\xf0\x00\x00<\x00\x00\xf0\x00\x00<\x00\x0f\x00\x00\x00C\xc0\x0f\x00\x00\x01\x03\xc00@\x00\x08\x0000\x08\x00@\x000\xc0\x00\x84\x00\x00\x0c\xc0\x00\x00\x00\x00\x0c\xfc\x00\x00\x00\x00\xfc\xfc\x00\x00\x00\x00\xfc\x03\xff\xc0\x0f\xff\x00\x03\xff\xc0\x0f\xff\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xff\xfc\x00\x00\x00\x00\xff\xfc\x00\x00')
        stella_bits = bytearray(b'\x06\x00\x09\x00\x09\x00p\xe0\x80\x10\x89\x10@  @F I 0\xc0')
        lettera_c_bits = bytearray(b'\x0f\xf8\x00\x10\x06\x00 \x01\x00@\x00\x80\x80\x00@\x80\xc0@\x81 @\x81 @\x81 @\x81 @\x81 @\x81 @\x81 @\x81 @\x81?\xc0\x81\x00\x00\x81\x00\x00\x81\x00\x00\x81\x00\x00\x81?\xc0\x81 @\x81 @\x81 @\x81 @\x81 @\x81 @\x81 @\x80\xc0@\x80\x00@@\x00\x80 \x01\x00\x10\x06\x00\x0f\xf8\x00')
        lettera_s_bits = bytearray(b'\x07\xf8\x008\x07\x00 \x01\x00@\x00\x80@\x00\x80\x80`\x80\x80\x90\x80\x80\x90\x80\x80\x90\x80\x80\x90\x80\x80\x8f\x00\x80@\x00\x80 \x00@\x18\x00@\x06\x00 \x01\x00\x10\x00\x80\x0c\x00@\x02\x00@\x01\x00@\x00\x80@~@@\x81 @\x81 @\x81 @\x81 @\x81 @\x80\xc0@@\x00@@\x00@ \x00\x80\x18\x03\x00\x07\xfc\x00')

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
    def show_header(self):
        # Orologio
        self.oled.text("12:12", 3, 3, 1)

        # Status Connettività WIFI
        self.oled.rect(109, 14, 3, 3, 1)
        self.oled.rect(113, 10, 3, 7, 1)
        self.oled.rect(117, 6, 3, 11, 1)
        self.oled.rect(121, 2, 3, 15, 1)

        self.show_header_data()

    # Aggiornamento dinamico delle componenti UI fisse in alto
    def show_header_data(self):
        pass

    # Layout e struttura della pagina informativa
    def show_stats_page(self):
        testaBatteria_bits = bytearray(b'\x1f\x001\x80 \x80\xe0\xe0')

        self.oled.text(self.AIR_HUMIDITY_LABEL, 3, 20, 1)

        self.oled.text(self.DIRT_MOISTURE_LABEL, 3, 29, 1)

        self.oled.text(self.TANK_LABEL, 85, 53, 1)

        self.oled.text(self.TEMPERATURE_LABEL, 3, 43, 1)

        self.oled.line(109, 49, 109, 29, 1)

        self.oled.line(121, 49, 121, 29, 1)

        fb_testaBatteria = framebuf.FrameBuffer(testaBatteria_bits, 11, 4, framebuf.MONO_HLSB)
        self.oled.blit(fb_testaBatteria, 110, 25)

        self.oled.line(110, 50, 120, 50, 1)

    # Dimensione delle stringhe scritte nello scorso rendering della
    # pagina di statistiche così da permettere un clear localizzato della superficie oled
    hum_width = 0
    moist_width = 0
    temp_width = 0

    # Aggiorniamo solo le informazioni dinamiche sulla pagina e non tutto il layout
    # in modo tale da usare solo le risorse minime ed indispensabili per il rendering
    def show_stats_data(self, sensor_data):
        pallinoGradi_bits = bytearray(b'@\xa0@')

        # Percentuale umidità dell'aria
        hum_str = f"{sensor_data["air_humidity"]:.1f}%"
        self.oled.rect(3 + self.AIR_HUMIDITY_LABEL_WIDTH, 20, self.hum_width, 8, 0, True) # pulizia del rect della stringa precedente
        self.hum_width = text_width(hum_str)
        self.oled.text(hum_str, 3 + self.AIR_HUMIDITY_LABEL_WIDTH, 20, 1)

        # Percentuale umidità del terreno
        moist_str = f"{sensor_data["soil_moisture"]:.1f}%"
        self.oled.rect(3 + self.DIRT_MOISTURE_LABEL_WIDTH, 29, self.moist_width, 8, 0, True) # pulizia del rect della stringa precedente
        self.moist_width = text_width(moist_str)
        self.oled.text(moist_str, 3 + self.DIRT_MOISTURE_LABEL_WIDTH, 29, 1)

        # Temperatura dell'aria
        temp_str = f"{sensor_data["air_temperature"]:.1f}"
        self.oled.rect(3 + self.TEMPERATURE_LABEL_WIDTH, 41, self.temp_width + 3 + 8, 10, 0, True) # pulizia del rect della stringa precedente
        self.moist_width = text_width(moist_str)
        self.oled.text(temp_str, 3 + self.TEMPERATURE_LABEL_WIDTH, 43, 1)
        self.temp_width = text_width(temp_str)

        fb_pallinoGradi = framebuf.FrameBuffer(pallinoGradi_bits, 3, 3, framebuf.MONO_HLSB)
        self.oled.blit(fb_pallinoGradi, 3 + self.TEMPERATURE_LABEL_WIDTH + self.temp_width, 41)
        self.oled.text("C", 3 + self.TEMPERATURE_LABEL_WIDTH + self.temp_width + 3, 43, 1) # il secondo + 3 proviene dalla dimensione del pallino per i gradi

        self.oled.show()
        # TESTA BATTERIA: (109,25)
        # BARRA1 : (111, 30), altezza 3, larghezza 9
        #
        # TACCA1 : (110, 15), (110, 15)
        # TACCA2 : (114, 15), (114, 11)
        # TACCA3 : (118, 15), (118, 7)
        # TACCA4 : (122, 15), (122, 3)
