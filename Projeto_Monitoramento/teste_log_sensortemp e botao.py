from machine import Pin, SPI, I2C
import time
from ssd1306 import SSD1306_I2C

# ------------------------------
# Display OLED SSD1306
# I2C1 -> SDA = GP14, SCL = GP15
# ------------------------------
i2c = I2C(1, scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)

# ------------------------------
# Configuração do botão no GP9
# ------------------------------
botao = Pin(9, Pin.IN, Pin.PULL_UP)

# ------------------------------
# Configuração do MAX6675 via SPI
# GP16 = MISO  (SO)
# GP17 = CS
# GP18 = SCK
# ------------------------------
cs = Pin(17, Pin.OUT)
cs.value(1)  # CS inativo

spi = SPI(
    0,
    baudrate=500000,
    polarity=0,
    phase=0,
    sck=Pin(18),
    mosi=Pin(19),  # o MAX6675 não usa MOSI, mas o SPI exige um pino
    miso=Pin(16)
)

# Função para ler temperatura
def ler_max6675():
    cs.value(0)          # Ativa o sensor
    data = spi.read(2)   # Lê 2 bytes
    cs.value(1)          # Desativa o sensor

    if data is None:
        return None

    valor = (data[0] << 8) | data[1]

    # Bit D2 indica se o termopar está conectado
    if valor & 0x04:
        return None  # sem termopar

    temp_c = (valor >> 3) * 0.25  # resolução do MAX6675
    return temp_c


print("Iniciando leitura do botão e do MAX6675...\n")

while True:
    # Leitura do botão (ativo em LOW)
    estado_botao = "PRESSIONADO" if botao.value() == 0 else "solto"

    # Leitura do MAX6675
    temperatura = ler_max6675()

    # ----------- PRINT NO TERMINAL -----------
    if temperatura is None:
        print(f"Botão: {estado_botao} | MAX6675: SEM SENSOR")
    else:
        print(f"Botão: {estado_botao} | Temperatura: {temperatura:.2f} °C")

    # ----------- MOSTRAR NO DISPLAY -----------
    oled.fill(0)
    oled.text("Botao:", 0, 0)
    oled.text(estado_botao, 60, 0)

    oled.text("Temp:", 0, 20)

    if temperatura is None:
        oled.text("SEM SENSOR", 60, 20)
    else:
        oled.text("{:.2f} C".format(temperatura), 60, 20)

    oled.show()

    time.sleep(0.5)
