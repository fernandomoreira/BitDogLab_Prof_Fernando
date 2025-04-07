from machine import Pin, ADC, PWM, SoftI2C
import neopixel
import utime
import random
from ssd1306 import SSD1306_I2C

# --- Configurações de Hardware ---
i2c_oled = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c_oled)

NUM_LEDS = 25
np = neopixel.NeoPixel(Pin(7), NUM_LEDS)

LED_MATRIX = [
    [24, 23, 22, 21, 20],
    [15, 16, 17, 18, 19],
    [14, 13, 12, 11, 10],
    [5, 6, 7, 8, 9],
    [4, 3, 2, 1, 0]
]

vrx = ADC(27)
vry = ADC(26)
botao = Pin(22, Pin.IN, Pin.PULL_UP)
buzzer = PWM(Pin(21))
buzzer.duty_u16(0)

# --- Variáveis do Jogo ---
x, y = 2, 2
target_x, target_y = random.randint(0, 4), random.randint(0, 4)
pontos = 0
pontos_fase1 = 0
game_over = False
fase = 1
start_time = utime.time()
ultimo_segundo = None
tempo_base = 0.2  # Fase 1: 0.2s, Fase 2: 0.1s
recordes = [0, 0, 0]
META_FASE1 = 30
TEMPO_FASE = 60

# --- Funções de Áudio ---
def beep(freq=1000, duration=100, volume=15000):
    buzzer.freq(freq)
    buzzer.duty_u16(volume)
    utime.sleep_ms(duration)
    buzzer.duty_u16(0)

def som_triste():
    for freq in [392, 349, 329, 293]:
        beep(freq, 200, 10000)
        utime.sleep_ms(50)
    beep(261, 500, 10000)

def som_vitoria():
    for freq in [523, 659, 784, 1047]:
        beep(freq, 150, 15000)
        utime.sleep_ms(50)

def beep_temporizador():
    global ultimo_segundo
    tempo_restante = TEMPO_FASE - (utime.time() - start_time)
    segundo_atual = int(tempo_restante)
    
    if segundo_atual != ultimo_segundo and 10 <= segundo_atual <= 60:
        if segundo_atual % 10 == 0 and segundo_atual != 10:
            beep(400, 150)
        else:
            beep(600, 80)
        ultimo_segundo = segundo_atual
    elif 0 < segundo_atual < 10:
        beep(800, 50 + segundo_atual * 10)
        utime.sleep_ms(100)

# --- Funções do Jogo ---
def animacao_acerto():
    for _ in range(2):
        for i in range(NUM_LEDS):
            np[i] = (0, 1, 0)  # Verde 2%
        np.write()
        utime.sleep(0.1)
        np.fill((0, 0, 0))
        np.write()
        utime.sleep(0.1)

def animacao_mudanca_fase():
    for _ in range(3):
        for i in range(NUM_LEDS):
            np[i] = (1, 1, 0)  # Amarelo 2%
        np.write()
        utime.sleep(0.15)
        np.fill((0, 0, 0))
        np.write()
        utime.sleep(0.15)

def desenha():
    if game_over:
        np.fill((0, 0, 0))
        np.write()
        return

    np.fill((0, 0, 0))
    np[LED_MATRIX[y][x]] = (1, 1, 1)       # Jogador
    np[LED_MATRIX[target_y][target_x]] = (1, 0, 0)  # Alvo
    np.write()

def carregar_recordes():
    try:
        with open('recordes.txt', 'r') as f:
            return [int(line.strip()) for line in f.readlines()]
    except:
        return [0, 0, 0]

def salvar_recordes():
    with open('recordes.txt', 'w') as f:
        for rec in recordes:
            f.write(str(rec) + '\n')

def atualizar_recordes(pontuacao):
    global recordes
    if pontuacao > recordes[0]:
        recordes = [pontuacao, recordes[0], recordes[1]]
    elif pontuacao > recordes[1]:
        recordes = [recordes[0], pontuacao, recordes[1]]
    elif pontuacao > recordes[2]:
        recordes[2] = pontuacao
    salvar_recordes()

def mostrar_menu():
    oled.fill(0)
    oled.text("RECORDES:", 0, 0)
    oled.text(f"1. {recordes[0]} pts", 0, 15)
    oled.text(f"2. {recordes[1]} pts", 0, 25)
    oled.text(f"3. {recordes[2]} pts", 0, 35)
    oled.text("Pressione START", 0, 50)
    oled.show()

def atualiza_display():
    oled.fill(0)
    tempo_restante = max(0, TEMPO_FASE - (utime.time() - start_time))
    
    oled.text(f"Fase {fase}: {int(tempo_restante)}s", 0, 0)
    oled.text(f"Pontos: {pontos}", 0, 20)
    oled.text(f"Meta: {META_FASE1 if fase == 1 else 'SOBREVIVA'}", 0, 40)
    
    if game_over:
        oled.text("GAME OVER!", 0, 55)
    oled.show()

def verifica_tempo():
    global fase, game_over, start_time, tempo_base, pontos_fase1
    
    tempo_decorrido = utime.time() - start_time
    
    if fase == 1 and pontos >= META_FASE1:
        fase = 2
        tempo_base = 0.1  # Aumenta velocidade
        pontos_fase1 = pontos
        animacao_mudanca_fase()
        som_vitoria()
        start_time = utime.time()  # Reseta timer para fase 2
    elif tempo_decorrido >= TEMPO_FASE:
        game_over = True
        if fase == 1:
            som_triste()
        atualizar_recordes(pontos_fase1 + pontos)

# --- Inicialização ---
recordes = carregar_recordes()
mostrar_menu()

# Espera início do jogo
while botao.value():
    utime.sleep(0.1)

# --- Loop principal ---
while True:
    if not game_over:
        desenha()
        atualiza_display()
        verifica_tempo()
        beep_temporizador()  # Funciona em ambas as fases agora

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
            beep(1500, 50)
            animacao_acerto()
            target_x, target_y = random.randint(0, 4), random.randint(0, 4)
            while target_x == x and target_y == y:
                target_x, target_y = random.randint(0, 4), random.randint(0, 4)

        utime.sleep(tempo_base)
    else:
        desenha()
        atualiza_display()
        if not botao.value():
            x, y = 2, 2
            pontos = 0
            pontos_fase1 = 0
            game_over = False
            fase = 1
            tempo_base = 0.2
            start_time = utime.time()
            ultimo_segundo = None
            utime.sleep(0.5)