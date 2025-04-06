from machine import Pin, ADC, PWM, SoftI2C
import neopixel
import utime
import random
from ssd1306 import SSD1306_I2C

# --- OLED ---
i2c_oled = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c_oled)

# --- Matriz de LEDs ---
NUM_LEDS = 25
np = neopixel.NeoPixel(Pin(7), NUM_LEDS)

LED_MATRIX = [
    [24, 23, 22, 21, 20],
    [15, 16, 17, 18, 19],
    [14, 13, 12, 11, 10],
    [5, 6, 7, 8, 9],
    [4, 3, 2, 1, 0]
]

# --- Joystick e buzzer ---
vrx = ADC(27)
vry = ADC(26)
botao = Pin(22, Pin.IN, Pin.PULL_UP)
buzzer = PWM(Pin(21))
buzzer.duty_u16(0)

# --- Estado inicial ---
x, y = 2, 2
target_x, target_y = random.randint(0, 4), random.randint(0, 4)
pontos = 0

# --- Funções ---
def bip():
    buzzer.freq(1000)
    buzzer.duty_u16(30000)
    utime.sleep(0.1)
    buzzer.duty_u16(0)

def atualiza_display(pontos):
    oled.fill(0)
    oled.text("PONTUACAO:", 0, 0)
    oled.text(str(pontos), 0, 15)
    oled.show()

def animacao_acerto():
    for _ in range(2):
        for i in range(NUM_LEDS):
            np[i] = (0, 40, 0)  # Verde suave
        np.write()
        utime.sleep(0.1)
        np.fill((0, 0, 0))
        np.write()
        utime.sleep(0.1)

def desenha():
    np.fill((0, 0, 0))  # Limpa LEDs

    cor_jogador = (
        random.randint(10, 40),
        random.randint(10, 40),
        random.randint(10, 40)
    )
    np[LED_MATRIX[y][x]] = cor_jogador  # Jogador com cor aleatória suave
    np[LED_MATRIX[target_y][target_x]] = (40, 0, 0)  # Alvo vermelho suave
    np.write()

print("Jogo iniciado. Pontue no OLED!")

# --- Loop principal ---
while True:
    desenha()
    atualiza_display(pontos)

    # Leitura joystick
    vx = vrx.read_u16()
    vy = vry.read_u16()

    if vx < 30000:
        x = max(0, x - 1)
    elif vx > 50000:
        x = min(4, x + 1)

    if vy < 30000:
        y = min(4, y + 1)
    elif vy > 50000:
        y = max(0, y - 1)

    # Checa colisão com alvo
    if x == target_x and y == target_y:
        pontos += 1
        bip()
        animacao_acerto()
        target_x, target_y = random.randint(0, 4), random.randint(0, 4)
        while target_x == x and target_y == y:
            target_x, target_y = random.randint(0, 4), random.randint(0, 4)

    # Dificuldade progressiva
    tempo = max(0.05, 0.2 - (pontos * 0.01))
    utime.sleep(tempo)
