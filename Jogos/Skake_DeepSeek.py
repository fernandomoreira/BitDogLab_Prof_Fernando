from machine import Pin, PWM, ADC
import neopixel
import utime
import random
from ssd1306 import SSD1306_I2C
from machine import SoftI2C

# --- Configurações de Hardware ---
# NeoPixel (Matriz 5x5)
np = neopixel.NeoPixel(Pin(7), 25)
LED_MATRIX = [
    [24, 23, 22, 21, 20],
    [15, 16, 17, 18, 19],
    [14, 13, 12, 11, 10],
    [5, 6, 7, 8, 9],
    [4, 3, 2, 1, 0]
]

# Buzzer
buzzer = PWM(Pin(10))

# Botões
botao_pausa = Pin(5, Pin.IN, Pin.PULL_UP)
botao_reset = Pin(6, Pin.IN, Pin.PULL_UP)

# Joystick
joy_x = ADC(27)
joy_y = ADC(26)
joy_btn = Pin(22, Pin.IN, Pin.PULL_UP)

# OLED
i2c = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c)

# --- Constantes do Jogo ---
LARGURA = 5
ALTURA = 5
DIR_CIMA = 0
DIR_DIREITA = 1
DIR_BAIXO = 2
DIR_ESQUERDA = 3

# --- Variáveis do Jogo ---
snake = [(2, 2)]  # Começa no centro
direcao = DIR_DIREITA
comida = None
pontos = 0
pausado = False
game_over = False

# --- Funções Auxiliares ---
def gerar_comida():
    while True:
        x = random.randint(0, LARGURA - 1)
        y = random.randint(0, ALTURA - 1)
        if (x, y) not in snake:
            return (x, y)

def atualizar_matriz():
    np.fill((0, 0, 0))  # Apaga todos os LEDs
    
    # Desenha a cobra (verde)
    for segmento in snake:
        x, y = segmento
        np[LED_MATRIX[y][x]] = (0, 20, 0)  # Verde
    
    # Desenha a comida (vermelho)
    if comida:
        x, y = comida
        np[LED_MATRIX[y][x]] = (20, 0, 0)  # Vermelho
    
    np.write()

def beep():
    buzzer.freq(1000)
    buzzer.duty_u16(30000)
    utime.sleep_ms(100)
    buzzer.duty_u16(0)

def ler_joystick():
    x = joy_x.read_u16()
    y = joy_y.read_u16()
    
    # Valores ajustados com eixo Y invertido
    if x < 10000: return DIR_ESQUERDA
    elif x > 50000: return DIR_DIREITA
    elif y > 50000: return DIR_CIMA  # Agora > 50000 é para CIMA
    elif y < 10000: return DIR_BAIXO  # Agora < 10000 é para BAIXO
    return None

def mostrar_oled():
    oled.fill(0)
    oled.text("Snake BitDogLab", 0, 0)
    oled.text(f"Pontos: {pontos}", 0, 20)
    if pausado: oled.text("PAUSADO", 0, 40)
    if game_over: oled.text("GAME OVER!", 0, 40)
    oled.show()

def reiniciar_jogo():
    global snake, direcao, comida, pontos, pausado, game_over
    snake = [(2, 2)]
    direcao = DIR_DIREITA
    comida = gerar_comida()
    pontos = 0
    pausado = False
    game_over = False

# --- Inicialização ---
comida = gerar_comida()
mostrar_oled()

# --- Loop Principal ---
while True:
    if not game_over:
        # Verifica botões
        if botao_reset.value() == 0:
            reiniciar_jogo()
            utime.sleep_ms(200)  # Debounce
        
        if botao_pausa.value() == 0:
            pausado = not pausado
            utime.sleep_ms(200)  # Debounce
        
        # Controle por joystick (agora com eixos corrigidos)
        nova_dir = ler_joystick()
        if nova_dir is not None and abs(nova_dir - direcao) != 2:
            direcao = nova_dir
        
        if not pausado:
            # Movimentação da cobra
            cabeca_x, cabeca_y = snake[0]
            
            if direcao == DIR_CIMA: cabeca_y -= 1
            elif direcao == DIR_DIREITA: cabeca_x += 1
            elif direcao == DIR_BAIXO: cabeca_y += 1
            elif direcao == DIR_ESQUERDA: cabeca_x -= 1
            
            # Modo infinito (teleporte nas bordas)
            cabeca_x %= LARGURA
            cabeca_y %= ALTURA
            
            nova_cabeca = (cabeca_x, cabeca_y)
            
            # Verifica colisão com o próprio corpo
            if nova_cabeca in snake:
                game_over = True
            else:
                snake.insert(0, nova_cabeca)
                
                # Verifica se comeu
                if nova_cabeca == comida:
                    beep()
                    pontos += 1
                    comida = gerar_comida()
                else:
                    snake.pop()  # Remove a cauda se não comeu
    
    # Atualiza hardware
    atualizar_matriz()
    mostrar_oled()
    utime.sleep_ms(500)  # Velocidade reduzida (era 300ms)