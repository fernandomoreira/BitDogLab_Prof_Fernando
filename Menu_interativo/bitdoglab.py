from machine import I2C, Timer, Pin

sdaPIN=Pin(0)
sclPIN=Pin(1)
i2c=I2C(0,sda=sdaPIN, scl=sclPIN, freq=100000)
timer_count = 0 # global variable

def interruption_handler(pin):
    global timer_count
    # Configuração dos botões
    button_a = Pin(5, Pin.IN, Pin.PULL_UP)
    button_b = Pin(6, Pin.IN, Pin.PULL_UP)
    if button_a.value() == 0 and button_b.value() == 0:
        timer_count += 1
    else:
        timer_count=0     
    if timer_count == 4:
        i2c.writeto_mem(107,24,b'2') 

class init():
    def __init__(self):
        soft_timer = Timer(mode=Timer.PERIODIC, period=1000, callback=interruption_handler)
        # limite de corrente 480mA = 6<<6 (6*80mA deslocado de 6 bits)
        #i2c.writeto_mem(107,2,b'384')
