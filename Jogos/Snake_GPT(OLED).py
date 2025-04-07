from machine import Pin, SoftI2C, ADC, PWM
from ssd1306 import SSD1306_I2C
import neopixel
import utime
import random

# --- OLED Display ---
i2c = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c)

# --- Joystick ---
x_axis = ADC(Pin(27))
y_axis = ADC(Pin(26))
sw_button = Pin(22, Pin.IN, Pin.PULL_UP)

# --- Botões ---
pause_button = Pin(5, Pin.IN, Pin.PULL_UP)
reset_button = Pin(6, Pin.IN, Pin.PULL_UP)

# --- Buzzer ---
buzzer = PWM(Pin(21))

def beep():
    buzzer.freq(1000)
    buzzer.duty_u16(30000)
    utime.sleep(0.1)
    buzzer.duty_u16(0)

def play_game_over_tone():
    notas = [196, 174, 155, 146, 130]  # Notas descendentes (tristes)
    for nota in notas:
        buzzer.freq(nota)
        buzzer.duty_u16(20000)
        utime.sleep(0.3)
        buzzer.duty_u16(0)
        utime.sleep(0.1)

# --- Matriz de LEDs RGB (NeoPixel 5x5) ---
NUM_LEDS = 25
np = neopixel.NeoPixel(Pin(7), NUM_LEDS)
LED_MATRIX = [
    [24, 23, 22, 21, 20],
    [15, 16, 17, 18, 19],
    [14, 13, 12, 11, 10],
    [5, 6, 7, 8, 9],
    [4, 3, 2, 1, 0]
]

# --- Redução de intensidade de LED (5%) ---
def dim(color, factor=0.05):
    return tuple(int(c * factor) for c in color)

# --- Efeitos Visuais ---
def effect_food():
    for _ in range(2):
        for i in range(NUM_LEDS):
            np[i] = dim((0, 255, 0))  # Verde suave
        np.write()
        utime.sleep(0.1)
        for i in range(NUM_LEDS):
            np[i] = (0, 0, 0)
        np.write()
        utime.sleep(0.1)

def effect_game_over():
    for step in range(5):
        for y in range(5):
            for x in range(5):
                if x + y == step:
                    led_index = LED_MATRIX[y][x]
                    np[led_index] = dim((255, 0, 0))  # Vermelho suave
        np.write()
        utime.sleep(0.1)
    
    play_game_over_tone()
    
    utime.sleep(0.5)
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    np.write()

# --- Jogo ---
CELL_SIZE = 4
WIDTH = 128 // CELL_SIZE
HEIGHT = 64 // CELL_SIZE

snake = [(WIDTH // 2, HEIGHT // 2)]
direction = (0, -1)
food = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
score = 0
paused = False
game_over = False

def read_joystick():
    x = x_axis.read_u16()
    y = y_axis.read_u16()
    if x > 60000:
        return (1, 0)
    elif x < 10000:
        return (-1, 0)
    elif y > 60000:
        return (0, -1)
    elif y < 10000:
        return (0, 1)
    return None

def draw():
    oled.fill(0)
    oled.fill_rect(food[0]*CELL_SIZE, food[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE, 1)
    for segment in snake:
        oled.fill_rect(segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE, 1)
    oled.text(f'Score:{score}', 0, 0)
    if paused:
        oled.text("PAUSADO", 40, 28)
    elif game_over:
        oled.text("GAME OVER", 30, 28)
    oled.show()

def update():
    global food, score, game_over
    head_x, head_y = snake[0]
    dx, dy = direction
    new_head = ((head_x + dx) % WIDTH, (head_y + dy) % HEIGHT)

    if new_head in snake:
        game_over = True
        effect_game_over()
        return

    snake.insert(0, new_head)

    if new_head == food:
        score += 1
        beep()
        effect_food()
        while food in snake:
            food = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
    else:
        snake.pop()

# --- Loop principal ---
last_move_time = utime.ticks_ms()

while True:
    if not pause_button.value():
        paused = not paused
        utime.sleep(0.3)  # debounce

    if not reset_button.value():
        snake = [(WIDTH // 2, HEIGHT // 2)]
        direction = (0, -1)
        food = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
        score = 0
        paused = False
        game_over = False
        np.fill((0, 0, 0))
        np.write()
        utime.sleep(0.3)

    if not paused and not game_over:
        new_dir = read_joystick()
        if new_dir and (new_dir[0] != -direction[0] or new_dir[1] != -direction[1]):
            direction = new_dir

        current_time = utime.ticks_ms()
        if utime.ticks_diff(current_time, last_move_time) > 200:
            update()
            last_move_time = current_time

    draw()
    utime.sleep(0.05)
