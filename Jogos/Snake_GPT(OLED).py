from machine import Pin, SoftI2C, ADC, PWM
from ssd1306 import SSD1306_I2C
import utime
import random

# --- Configurações do display OLED ---
i2c = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c)

# --- Configurações do joystick ---
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

# --- Variáveis iniciais ---
CELL_SIZE = 4
WIDTH = 128 // CELL_SIZE
HEIGHT = 64 // CELL_SIZE

snake = [(WIDTH//2, HEIGHT//2)]
direction = (0, -1)
food = (random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1))
score = 0
paused = False
game_over = False

# --- Leitura do joystick ---
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

# --- Desenho na tela ---
def draw():
    oled.fill(0)
    # desenha comida
    oled.fill_rect(food[0]*CELL_SIZE, food[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE, 1)
    # desenha cobra
    for segment in snake:
        oled.fill_rect(segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE, 1)
    oled.text(f'Score:{score}', 0, 0)
    if paused:
        oled.text("PAUSADO", 40, 28)
    elif game_over:
        oled.text("GAME OVER", 30, 28)
    oled.show()

# --- Movimenta a cobra ---
def update():
    global food, score, game_over

    head_x, head_y = snake[0]
    dx, dy = direction
    new_head = ((head_x + dx) % WIDTH, (head_y + dy) % HEIGHT)

    if new_head in snake:
        game_over = True
        return

    snake.insert(0, new_head)

    if new_head == food:
        score += 1
        beep()
        while food in snake:
            food = (random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1))
    else:
        snake.pop()

# --- Loop principal ---
last_move_time = utime.ticks_ms()

while True:
    if not pause_button.value():
        paused = not paused
        utime.sleep(0.3)  # debounce

    if not reset_button.value():
        snake = [(WIDTH//2, HEIGHT//2)]
        direction = (0, -1)
        food = (random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1))
        score = 0
        paused = False
        game_over = False
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
