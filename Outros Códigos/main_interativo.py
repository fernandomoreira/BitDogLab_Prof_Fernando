from machine import Pin, SoftI2C, ADC
from ssd1306 import SSD1306_I2C
import os
import utime

# OLED
i2c = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c)

# Joystick
y_axis = ADC(Pin(26))
joystick_button = Pin(22, Pin.IN, Pin.PULL_UP)  # SW

# Botão B
button_b = Pin(6, Pin.IN, Pin.PULL_UP)

# Estado de navegação
current_path = "/"
selecionado = 0

def listar_conteudo(path):
    try:
        itens = os.listdir(path)
    except:
        return []
    entradas = []
    for item in itens:
        full_path = path + "/" + item if path != "/" else item
        if os.stat(full_path)[0] & 0x4000:  # é diretório
            entradas.append((item + "/", True))
        elif item.endswith(".py"):
            entradas.append((item, False))
    return sorted(entradas, key=lambda x: (not x[1], x[0].lower()))

def desenhar_menu(itens):
    oled.fill(0)
    titulo = "Menu: " + current_path if current_path != "/" else "Menu Principal"
    oled.text(titulo[:20], 0, 0)
    for i in range(min(4, len(itens))):
        idx = (selecionado + i) % len(itens)
        nome, is_dir = itens[idx]
        prefixo = ">" if i == 0 else " "
        sufixo = "/" if is_dir else ""
        oled.text(f"{prefixo} {nome[:14]}", 0, 12 + i*10)
    oled.show()

def joystick_cima():
    return y_axis.read_u16() < 10000

def joystick_baixo():
    return y_axis.read_u16() > 60000

def executar_programa(path):
    oled.fill(0)
    oled.text("Executando:", 0, 10)
    oled.text(path[-20:], 0, 25)
    oled.show()
    utime.sleep(1)
    try:
        with open(path) as f:
            exec(f.read(), {})
    except Exception as e:
        oled.fill(0)
        oled.text("Erro ao executar", 0, 10)
        oled.text(path[-20:], 0, 25)
        oled.text(str(e)[:20], 0, 45)
        oled.show()
        utime.sleep(3)

# --- Loop principal ---
ultimo_mov = utime.ticks_ms()

while True:
    conteudo = listar_conteudo(current_path)
    if not conteudo:
        oled.fill(0)
        oled.text("Pasta vazia!", 0, 25)
        oled.show()
        utime.sleep(1)
        current_path = "/"
        selecionado = 0
        continue

    desenhar_menu(conteudo)
    agora = utime.ticks_ms()

    # Navegação
    if joystick_cima() and utime.ticks_diff(agora, ultimo_mov) > 200:
        selecionado = (selecionado - 1) % len(conteudo)
        ultimo_mov = agora

    if joystick_baixo() and utime.ticks_diff(agora, ultimo_mov) > 200:
        selecionado = (selecionado + 1) % len(conteudo)
        ultimo_mov = agora

    # Abrir ou Executar
    if not button_b.value():
        nome, is_dir = conteudo[selecionado]
        if is_dir:
            current_path = current_path + "/" + nome if current_path != "/" else nome
            selecionado = 0
        else:
            caminho_completo = current_path + "/" + nome if current_path != "/" else nome
            executar_programa(caminho_completo)
        utime.sleep(0.3)

    # Voltar com botão do joystick (SW)
    if not joystick_button.value():
        if current_path != "/":
            partes = current_path.strip("/").split("/")
            current_path = "/" if len(partes) == 1 else "/".join(partes[:-1])
            selecionado = 0
        utime.sleep(0.3)

    utime.sleep(0.05)

