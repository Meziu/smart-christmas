import utime


# Helper per il fuso orario italiano (posto che funzioni la sincronizzazione NTP)
def localtime_italy():
    t = utime.localtime()
    return utime.localtime(utime.mktime(t) + 3600)


def localtime_italy_str():
    t = localtime_italy()
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
    )


# Helper per ottenere le dimensioni sullo schermo del testo.
def text_width(text):
    return len(text) * 8


music = [
    ("Jingle Bells", 12800),
    ("WWY a Merry Christmas", 9600),
    ("Let It Snow", 11700),
]
