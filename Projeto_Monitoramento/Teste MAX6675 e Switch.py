from machine import Pin, SPI
import time

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

    if temperatura is None:
        print(f"Botão: {estado_botao} | MAX6675: SEM SENSOR")
    else:
        print(f"Botão: {estado_botao} | Temperatura: {temperatura:.2f} °C")

    time.sleep(0.5)
