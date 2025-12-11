from machine import Pin, I2C
import ssd1306
import framebuf

class DisplayManager():
    OLED_WIDTH = 128
    OLED_HEIGHT = 64

    def __init__(self):
        # ESP32 Pin assignment to OLED
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21))

        self.oled = ssd1306.SSD1306_I2C(self.OLED_WIDTH, self.OLED_HEIGHT, self.i2c)

    def show_logo(self):
        image_Layer_1_bits = bytearray(b'\x00\x00\x03\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x0c\xc0\x00\x00\x00\x00\x0c\xc0\x00\x00\x00\x0000\x00\x00\x00\x0000\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x03\x00\x03\x00\x00\x00\x03\x00\x0b\x00\x00\x00\x0c\x00 \xc0\x00\x00\x0d\x00\x80\xc0\x00\x000$\x000\x00\x000\x00\x000\x00\x00<\x00\x00\xf0\x00\x00<\x00\x00\xf0\x00\x00\x03\xc0\x0f\x00\x00\x00\x03\xc0\x0f\x00\x00\x00\x0f\x00\x03\xc0\x00\x00\x0f\x00\x03\xc0\x00\x00\xf0\x00\x00<\x00\x00\xf4\x00\x00<\x00\x03\x01\x00\x00C\x00\x03\x00 \x02\x03\x00\x0c\x00\x02 \x00\xc0\x0c\x00\x00\x00\x00\xc0\x0f\xc0\x00\x00\x0f\xc0\x0f\xc0\x00\x00\x0f\xc0\x00<\x00\x00\xf0\x00\x00<\x00\x00\xf0\x00\x00\xf0\x00\x00<\x00\x00\xf0\x00\x00<\x00\x0f\x00\x00\x00C\xc0\x0f\x00\x00\x01\x03\xc00@\x00\x08\x0000\x08\x00@\x000\xc0\x00\x84\x00\x00\x0c\xc0\x00\x00\x00\x00\x0c\xfc\x00\x00\x00\x00\xfc\xfc\x00\x00\x00\x00\xfc\x03\xff\xc0\x0f\xff\x00\x03\xff\xc0\x0f\xff\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xc0\x0c\x00\x00\x00\x00\xff\xfc\x00\x00\x00\x00\xff\xfc\x00\x00')
        image_Layer_2_bits = bytearray(b'\x06\x00\x09\x00\x09\x00p\xe0\x80\x10\x89\x10@  @F I 0\xc0')
        image_Layer_3_bits = bytearray(b'\x0f\xf8\x00\x10\x06\x00 \x01\x00@\x00\x80\x80\x00@\x80\xc0@\x81 @\x81 @\x81 @\x81 @\x81 @\x81 @\x81 @\x81 @\x81?\xc0\x81\x00\x00\x81\x00\x00\x81\x00\x00\x81\x00\x00\x81?\xc0\x81 @\x81 @\x81 @\x81 @\x81 @\x81 @\x81 @\x80\xc0@\x80\x00@@\x00\x80 \x01\x00\x10\x06\x00\x0f\xf8\x00')
        image_Layer_4_bits = bytearray(b'\x07\xf8\x008\x07\x00 \x01\x00@\x00\x80@\x00\x80\x80`\x80\x80\x90\x80\x80\x90\x80\x80\x90\x80\x80\x90\x80\x80\x8f\x00\x80@\x00\x80 \x00@\x18\x00@\x06\x00 \x01\x00\x10\x00\x80\x0c\x00@\x02\x00@\x01\x00@\x00\x80@~@@\x81 @\x81 @\x81 @\x81 @\x81 @\x80\xc0@@\x00@@\x00@ \x00\x80\x18\x03\x00\x07\xfc\x00')

        fb_image_Layer_1_bits = framebuf.FrameBuffer(image_Layer_1_bits, 46, 50, framebuf.MONO_HLSB)
        self.oled.blit(fb_image_Layer_1_bits, 42, 11)

        fb_image_Layer_2_bits = framebuf.FrameBuffer(image_Layer_2_bits, 12, 11, framebuf.MONO_HLSB)
        self.oled.blit(fb_image_Layer_2_bits, 59, 3)

        fb_image_Layer_3_bits = framebuf.FrameBuffer(image_Layer_3_bits, 18, 33, framebuf.MONO_HLSB)
        self.oled.blit(fb_image_Layer_3_bits, 100, 15)

        fb_image_Layer_4_bits = framebuf.FrameBuffer(image_Layer_4_bits, 18, 33, framebuf.MONO_HLSB)
        self.oled.blit(fb_image_Layer_4_bits, 10, 15)

        self.oled.show()

    def show_stats_page(self):
        image_pallinoGradi_bits = bytearray(b'@\xa0@')
        image_testaBatteria_bits = bytearray(b'\x1f\x001\x80 \x80\xe0\xe0')

        self.oled.text("12:12", 3, 3, 1)

        self.oled.text("Terra:56%", 3, 29, 1)

        self.oled.text("Umid.", 3, 20, 1)

        self.oled.text("Acqua", 85, 53, 1)

        self.oled.text("Temp:34", 3, 43, 1)

        self.oled.text("C", 67, 43, 1)

        fb_image_pallinoGradi_bits = framebuf.FrameBuffer(image_pallinoGradi_bits, 3, 3, framebuf.MONO_HLSB)
        self.oled.blit(fb_image_pallinoGradi_bits, 64, 41)

        self.oled.line(109, 49, 109, 29, 1)

        self.oled.line(121, 49, 121, 29, 1)

        self.oled.rect(109, 14, 3, 3, 1)

        fb_image_testaBatteria_bits = framebuf.FrameBuffer(image_testaBatteria_bits, 11, 4, framebuf.MONO_HLSB)
        self.oled.blit(fb_image_testaBatteria_bits, 110, 25)

        self.oled.rect(113, 10, 3, 7, 1)

        self.oled.rect(117, 6, 3, 11, 1)

        self.oled.rect(121, 2, 3, 15, 1)

        self.oled.line(110, 50, 120, 50, 1)

        self.oled.show()

    def show_stats_data():
        pass
        # TESTA BATTERIA: (109,25)
        # BARRA1 : (111, 30), altezza 3, larghezza 9
        #
        # TACCA1 : (110, 15), (110, 15)
        # TACCA2 : (114, 15), (114, 11)
        # TACCA3 : (118, 15), (118, 7)
        # TACCA4 : (122, 15), (122, 3)
