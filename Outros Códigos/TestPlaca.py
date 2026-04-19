# ============================================================
#  TESTE COMPLETO DE HARDWARE - BitDogLab V7
#  MicroPython - Raspberry Pi Pico H/W
#
#  DISPLAY: SSD1306 128x64  SDA=GP14  SCL=GP15
#  (conforme biblioteca ssd1306.py fornecida)
#
#  Para rodar SEM PC: salve este arquivo como main.py
#  na raiz da placa. Ele aguarda 4s ao ligar antes de iniciar.
#
#  Testes executados:
#   1.  Display OLED
#   2.  LED RGB        (GP13, GP11, GP12)
#   3.  Botoes A/B/C   (GP10, GP5, GP6)
#   4.  Buzzer         (GP21)
#   5.  Neopixel 5x5   (GP7)
#   6.  Joystick       (GP27, GP26, GP22)
#   7.  Microfone      (GP28)
#   8.  Sensores internos RP2040 (temperatura do chip)
#   9.  Nivel de bateria / VSYS  (GP29 interno)
#  10.  Scan I2C       (I2C0 e I2C1)
#  11.  LED onboard
# ============================================================

from machine import Pin, PWM, I2C, ADC, SoftI2C
import neopixel
import utime
import math

# ------------------------------------------------------------
# PAUSA INICIAL - permite abrir terminal/Thonny antes de rodar
# Reduza para 0 se quiser arranque imediato standalone
# ------------------------------------------------------------
utime.sleep(4)

# ------------------------------------------------------------
# DISPLAY SSD1306
# Pinos conforme a biblioteca entregue: SDA=GP14  SCL=GP15
# ------------------------------------------------------------
from ssd1306 import SSD1306_I2C

i2c_oled = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c_oled)

# ============================================================
# UTILITARIOS DE DISPLAY
# ============================================================

def d_clear():
    oled.fill(0)

def d_show():
    oled.show()

def d_header(titulo, sub=""):
    oled.fill(0)
    oled.fill_rect(0, 0, 128, 13, 1)
    oled.text(titulo[:16], 0, 3, 0)
    if sub:
        oled.text(sub[:16], 0, 16, 1)
    oled.show()

def d_linha(row, texto, destaque=False):
    y = 16 + row * 10
    if y + 8 > 64:
        return
    oled.fill_rect(0, y, 128, 10, 1 if destaque else 0)
    oled.text(texto[:16], 0, y + 1, 0 if destaque else 1)
    oled.show()

def d_barra(row, pct, label=""):
    y = 16 + row * 10
    if y + 8 > 64:
        return
    oled.fill_rect(0, y, 128, 10, 0)
    largura = max(1, int(126 * pct / 100))
    oled.rect(0, y + 1, 126, 8, 1)
    oled.fill_rect(1, y + 2, largura, 6, 1)
    if label:
        oled.text(label[:8], 2, y + 2, 0 if largura > 44 else 1)
    oled.show()

def d_resultado(nome, resultado, detalhe=""):
    oled.fill(0)
    oled.fill_rect(0, 0, 128, 13, 1)
    oled.text(nome[:16], 0, 3, 0)
    if resultado == "OK":
        oled.text("[  OK  ]", 24, 20, 1)
    else:
        oled.fill_rect(0, 15, 128, 14, 1)
        oled.text("[ FALHA ]", 20, 19, 0)
    if detalhe:
        oled.text(detalhe[:16], 0, 36, 1)
        if len(detalhe) > 16:
            oled.text(detalhe[16:32], 0, 46, 1)
    oled.show()
    utime.sleep_ms(2500)

def d_espera(l1, l2="", l3="", seg=0):
    oled.fill(0)
    oled.fill_rect(0, 0, 128, 13, 1)
    oled.text("AGUARDANDO...", 0, 3, 0)
    oled.text(l1[:16], 0, 16, 1)
    if l2:
        oled.text(l2[:16], 0, 26, 1)
    if l3:
        oled.text(l3[:16], 0, 36, 1)
    if seg:
        oled.text("Tempo: " + str(seg) + "s", 0, 50, 1)
    oled.show()

def d_resumo(res):
    ok   = sum(1 for v in res.values() if v == "OK")
    fail = sum(1 for v in res.values() if v == "FAIL")
    oled.fill(0)
    oled.fill_rect(0, 0, 128, 13, 1)
    oled.text("RESUMO FINAL", 0, 3, 0)
    oled.text("Aprovados: " + str(ok),   0, 16, 1)
    oled.text("Falhas:    " + str(fail), 0, 26, 1)
    oled.text("Total:     " + str(len(res)), 0, 36, 1)
    if fail == 0:
        oled.text("** APROVADA **", 8, 52, 1)
    else:
        oled.fill_rect(0, 49, 128, 14, 1)
        oled.text("!! COM FALHAS !!", 0, 52, 0)
    oled.show()

def log(msg):
    print(msg)

def log_res(nome, res, det=""):
    s = " [OK]  " if res == "OK" else " [FAIL]"
    print(s + " " + nome + (" | " + det if det else ""))

# ============================================================
# TESTES
# ============================================================

# ------------------------------------------------------------
# 1. DISPLAY OLED
# ------------------------------------------------------------
def teste_display():
    N = "DISPLAY OLED"
    log("\n=== " + N + " ===")
    d_header(N, "SSD1306 128x64")
    utime.sleep_ms(1000)
    d_linha(0, "SDA: GP14")
    utime.sleep_ms(700)
    d_linha(1, "SCL: GP15")
    utime.sleep_ms(700)
    d_linha(2, "Addr: 0x3C")
    utime.sleep_ms(700)
    d_linha(3, "Teste visual...")
    utime.sleep_ms(800)

    # xadrez
    oled.fill(0)
    for x in range(0, 128, 8):
        for y in range(0, 64, 8):
            if (x // 8 + y // 8) % 2 == 0:
                oled.fill_rect(x, y, 8, 8, 1)
    oled.show()
    utime.sleep_ms(1000)

    # tela cheia
    oled.fill(1); oled.show(); utime.sleep_ms(500)
    oled.fill(0); oled.show(); utime.sleep_ms(400)

    d_resultado(N, "OK", "Imagem visivel?")
    log_res(N, "OK")
    return "OK"

# ------------------------------------------------------------
# 2. LED RGB
# ------------------------------------------------------------
def teste_led_rgb():
    N = "LED RGB"
    log("\n=== " + N + " ===")
    d_header(N, "R=GP13 G=GP11 B=GP12")

    r = PWM(Pin(13)); r.freq(1000)
    g = PWM(Pin(11)); g.freq(1000)
    b = PWM(Pin(12)); b.freq(1000)

    def rgb(rv, gv, bv):
        r.duty_u16(rv); g.duty_u16(gv); b.duty_u16(bv)

    cores = [
        ("Vermelho",  65535,     0,     0),
        ("Verde",         0, 65535,     0),
        ("Azul",          0,     0, 65535),
        ("Amarelo",   65535, 38000,     0),
        ("Ciano",         0, 65535, 65535),
        ("Magenta",   65535,     0, 65535),
        ("Branco",    60000, 60000, 60000),
        ("Apagando",      0,     0,     0),
    ]

    utime.sleep_ms(600)
    for i, (nome, rv, gv, bv) in enumerate(cores):
        d_linha(0, "Cor: " + nome)
        d_barra(2, int((i + 1) * 100 / len(cores)),
                str(i + 1) + "/" + str(len(cores)))
        rgb(rv, gv, bv)
        utime.sleep_ms(800)

    rgb(0, 0, 0)
    r.deinit(); g.deinit(); b.deinit()
    d_resultado(N, "OK", "Cores visiveis?")
    log_res(N, "OK")
    return "OK"

# ------------------------------------------------------------
# 3. BOTOES A, B, C
# ------------------------------------------------------------
def teste_botoes():
    N = "BOTOES A B C"
    log("\n=== " + N + " ===")

    btn = {
        "A": Pin(10, Pin.IN, Pin.PULL_UP),
        "B": Pin(5,  Pin.IN, Pin.PULL_UP),
        "C": Pin(6,  Pin.IN, Pin.PULL_UP),
    }
    det = {"A": False, "B": False, "C": False}

    def tela():
        oled.fill(0)
        oled.fill_rect(0, 0, 128, 13, 1)
        oled.text(N, 0, 3, 0)
        for i, (k, v) in enumerate(det.items()):
            oled.fill_rect(0, 16 + i * 12, 128, 12, 1 if v else 0)
            oled.text(("[OK] " if v else "[  ] ") + "Botao " + k,
                      0, 17 + i * 12, 0 if v else 1)
        falt = [k for k, v in det.items() if not v]
        msg = "Falta: " + " ".join(falt) if falt else "Todos OK!"
        oled.text(msg[:16], 0, 54, 1)
        oled.show()

    tela()
    deadline = utime.ticks_add(utime.ticks_ms(), 10000)

    while utime.ticks_diff(deadline, utime.ticks_ms()) > 0:
        for k, p in btn.items():
            if not det[k] and p.value() == 0:
                det[k] = True
                log("  Botao " + k + " OK")
                tela()
                utime.sleep_ms(200)
        if all(det.values()):
            break
        utime.sleep_ms(50)

    res = "OK" if all(det.values()) else "FAIL"
    falt = [k for k, v in det.items() if not v]
    det_str = "Todos OK" if res == "OK" else "Faltou:" + " ".join(falt)
    d_resultado(N, res, det_str)
    log_res(N, res, det_str)
    return res

# ------------------------------------------------------------
# 4. BUZZER
# ------------------------------------------------------------
def teste_buzzer():
    N = "BUZZER"
    log("\n=== " + N + " ===")
    d_header(N, "GPIO 21")
    utime.sleep_ms(800)

    bz = PWM(Pin(21))
    notas = [
        ("Do  262Hz", 262), ("Re  294Hz", 294),
        ("Mi  330Hz", 330), ("Fa  349Hz", 349),
        ("Sol 392Hz", 392), ("La  440Hz", 440),
        ("Si  494Hz", 494), ("Do  523Hz", 523),
    ]

    for i, (nome_n, freq) in enumerate(notas):
        d_linha(0, nome_n)
        d_barra(2, int((i + 1) * 100 / len(notas)),
                str(i + 1) + "/" + str(len(notas)))
        bz.freq(freq); bz.duty_u16(28000)
        utime.sleep_ms(300)
        bz.duty_u16(0); utime.sleep_ms(80)

    # Jingle final
    d_linha(0, "Jingle final...")
    for freq, dur in [(523,120),(523,120),(587,280),(523,280),(698,280),(659,480)]:
        bz.freq(freq); bz.duty_u16(25000)
        utime.sleep_ms(dur)
        bz.duty_u16(0); utime.sleep_ms(60)

    bz.deinit()
    d_resultado(N, "OK", "Som audivel?")
    log_res(N, "OK")
    return "OK"

# ------------------------------------------------------------
# 5. NEOPIXEL 5x5
# ------------------------------------------------------------
LED_MATRIX = [
    [24,23,22,21,20],
    [15,16,17,18,19],
    [14,13,12,11,10],
    [ 5, 6, 7, 8, 9],
    [ 4, 3, 2, 1, 0],
]

def teste_neopixel():
    N = "NEOPIXEL 5x5"
    log("\n=== " + N + " ===")
    d_header(N, "GP7 - 25 LEDs")
    utime.sleep_ms(800)

    np = neopixel.NeoPixel(Pin(7), 25)

    def apaga():
        for i in range(25): np[i] = (0, 0, 0)
        np.write()

    cores = [(50,0,0),(0,50,0),(0,0,50),(50,40,0),(0,40,40)]

    # Varredura por linha
    d_linha(0, "Varredura linhas")
    for li, linha in enumerate(LED_MATRIX):
        d_barra(2, int((li + 1) * 100 / 5), "Linha " + str(li + 1))
        for idx in linha: np[idx] = cores[li]
        np.write()
        utime.sleep_ms(500)
    utime.sleep_ms(400)
    apaga(); utime.sleep_ms(300)

    # LED a LED
    d_linha(0, "LED por LED")
    for i in range(25):
        np[i] = (25, 25, 25)
        np.write()
        d_barra(2, int((i + 1) * 100 / 25), str(i + 1) + "/25")
        utime.sleep_ms(100)
    utime.sleep_ms(400)

    # Pisca verde
    d_linha(0, "Pisca 3x verde")
    for _ in range(3):
        for i in range(25): np[i] = (0, 50, 0)
        np.write(); utime.sleep_ms(350)
        apaga(); utime.sleep_ms(200)

    apaga()
    d_resultado(N, "OK", "LEDs visiveis?")
    log_res(N, "OK")
    return "OK"

# ------------------------------------------------------------
# 6. JOYSTICK
# ------------------------------------------------------------
def teste_joystick():
    N = "JOYSTICK"
    log("\n=== " + N + " ===")

    vrx = ADC(Pin(27))
    vry = ADC(Pin(26))
    sw  = Pin(22, Pin.IN, Pin.PULL_UP)

    sw_ok  = False
    lx, ly = [], []

    d_espera("Mova o joystick",
             "em todas direcoes",
             "e pressione SW",
             seg=8)
    utime.sleep_ms(1000)

    deadline = utime.ticks_add(utime.ticks_ms(), 8000)

    while utime.ticks_diff(deadline, utime.ticks_ms()) > 0:
        x = vrx.read_u16(); y = vry.read_u16()
        lx.append(x); ly.append(y)

        px = int(x / 655)
        py = 100 - int(y / 655)          # invertido: cima=100, baixo=0

        oled.fill(0)
        oled.fill_rect(0, 0, 128, 13, 1)
        oled.text("JOYSTICK", 0, 3, 0)
        oled.text("VRx: " + str(px) + "%", 0, 16, 1)
        oled.text("VRy: " + str(py) + "%", 0, 26, 1)
        # mini mapa de posicao 40x40
        cx, cy = 94, 38
        oled.rect(cx - 20, cy - 20, 40, 40, 1)
        dpx = cx - 19 + int(38 * x / 65535)
        dpy = cy + 19 - int(38 * y / 65535)  # invertido: y alto = ponto acima
        oled.fill_rect(dpx - 2, dpy - 2, 5, 5, 1)

        sw_lido = sw.value() == 0
        if sw_lido:
            sw_ok = True
        sw_txt = "SW: OK!" if sw_ok else "SW: aguard."
        oled.text(sw_txt, 0, 36, 1)

        rest = utime.ticks_diff(deadline, utime.ticks_ms()) // 1000
        oled.text("Tempo: " + str(rest) + "s", 0, 54, 1)
        oled.show()
        utime.sleep_ms(80)

    vx = max(lx) - min(lx)
    vy = max(ly) - min(ly)
    analog_ok = vx > 5000 or vy > 5000
    res = "OK" if analog_ok else "FAIL"
    det = ("Analog OK" if analog_ok else "Analog --") + (" SW:OK" if sw_ok else " SW:--")
    log("  VarX=" + str(vx) + " VarY=" + str(vy) + " SW=" + str(sw_ok))
    d_resultado(N, res, det)
    log_res(N, res, det)
    return res

# ------------------------------------------------------------
# 7. MICROFONE
# ------------------------------------------------------------
def teste_microfone():
    N = "MICROFONE"
    log("\n=== " + N + " ===")

    mic = ADC(Pin(28))
    AMOSTRAS = 300

    d_espera("Fale ou bata palma",
             "perto do microfone",
             "",
             seg=5)
    utime.sleep_ms(1800)

    d_header(N, "GP28 - coletando")
    amostras = []
    for i in range(AMOSTRAS):
        amostras.append(mic.read_u16())
        if i % 30 == 0:
            pct = int(i * 100 / AMOSTRAS)
            d_barra(1, pct, str(pct) + "%")
        utime.sleep_ms(5)

    medio    = sum(amostras) // len(amostras)
    variacao = max(amostras) - min(amostras)
    soma_sq  = sum((a - medio) ** 2 for a in amostras)
    rms      = int(math.sqrt(soma_sq // len(amostras)))

    d_header(N, "Resultados")
    d_linha(0, "Medio: " + str(medio))
    d_linha(1, "Variacao: " + str(variacao))
    d_linha(2, "RMS:  " + str(rms))
    utime.sleep_ms(2000)

    medio_ok = 10000 < medio < 55000
    ruido_ok = variacao > 400
    res = "OK" if (medio_ok and ruido_ok) else "FAIL"
    det = "Med=" + str(medio // 100) + " V=" + str(variacao)
    log("  Medio=" + str(medio) + " Var=" + str(variacao) + " RMS=" + str(rms))
    d_resultado(N, res, det)
    log_res(N, res, det)
    return res

# ------------------------------------------------------------
# 8. SENSORES INTERNOS RP2040
#    - Temperatura interna do chip (ADC canal 4)
#    - Referencia interna (ADC canal 3)
# ------------------------------------------------------------
def teste_sensores_internos():
    N = "CHIP INTERNO"
    log("\n=== " + N + " ===")
    d_header(N, "RP2040 on-chip")
    utime.sleep_ms(800)

    s_temp = ADC(4)
    s_vref = ADC(3)

    lt, lv = [], []
    d_linha(0, "Coletando 20x...")
    for i in range(20):
        lt.append(s_temp.read_u16())
        lv.append(s_vref.read_u16())
        d_barra(2, int((i + 1) * 100 / 20), str(i + 1) + "/20")
        utime.sleep_ms(120)

    adc_t = sum(lt) / len(lt)
    v_t   = adc_t * (3.3 / 65535)
    temp  = 27.0 - (v_t - 0.706) / 0.001721

    adc_v = sum(lv) / len(lv)
    v_ref = adc_v * (3.3 / 65535)

    t_str = str(int(temp * 10) / 10) + "C"
    v_str = str(int(v_ref * 1000)) + "mV"

    d_header(N, "Resultados")
    d_linha(0, "Temp.chip: " + t_str)
    d_linha(1, "VREF:      " + v_str)
    d_linha(2, "ADC temp: " + str(int(adc_t)))
    utime.sleep_ms(2000)

    temp_ok = 10.0 < temp < 75.0
    res = "OK" if temp_ok else "FAIL"
    log("  Temp=" + t_str + " VREF=" + v_str)
    d_resultado(N, res, "T=" + t_str + " V=" + v_str)
    log_res(N, res, "Temp=" + t_str)
    return res

# ------------------------------------------------------------
# 9. NIVEL DE BATERIA / VSYS (GP29 interno do Pico)
#    VSYS passa por divisor 1/3 interno antes do ADC.
#    Tensao real = leitura_adc * (3.3/65535) * 3
# ------------------------------------------------------------
def teste_bateria():
    N = "BATERIA/VSYS"
    log("\n=== " + N + " ===")
    d_header(N, "GP29 - VSYS/3")
    utime.sleep_ms(800)

    try:
        vsys = ADC(29)
    except Exception:
        d_resultado(N, "FAIL", "ADC29 indispon.")
        log_res(N, "FAIL", "ADC29 indisponivel")
        return "FAIL"

    leituras = []
    d_linha(0, "Medindo VSYS...")
    for i in range(30):
        leituras.append(vsys.read_u16())
        d_barra(2, int((i + 1) * 100 / 30), str(i + 1) + "/30")
        utime.sleep_ms(60)

    media  = sum(leituras) // len(leituras)
    v_vsys = media * (3.3 / 65535) * 3

    if v_vsys >= 4.5:
        fonte = "USB/Fonte"
        pct   = 100
    elif v_vsys >= 4.0:
        fonte = "Bat. boa"
        pct   = 90
    elif v_vsys >= 3.7:
        fonte = "Bat. media"
        pct   = 60
    elif v_vsys >= 3.4:
        fonte = "Bat. baixa"
        pct   = 20
    else:
        fonte = "Critico!"
        pct   = 5

    v_str = str(int(v_vsys * 100) / 100) + "V"

    d_header(N, fonte)
    d_linha(0, "VSYS: " + v_str)
    d_barra(2, pct, str(pct) + "%")
    d_linha(3, fonte)
    utime.sleep_ms(2000)

    res = "OK" if v_vsys > 3.0 else "FAIL"
    log("  VSYS=" + v_str + " (" + fonte + ") " + str(pct) + "%")
    d_resultado(N, res, "VSYS=" + v_str)
    log_res(N, res, "VSYS=" + v_str)
    return res

# ------------------------------------------------------------
# 10. SCAN I2C
# ------------------------------------------------------------
def teste_i2c_scan():
    N = "I2C SCAN"
    log("\n=== " + N + " ===")
    d_header(N, "I2C0 e I2C1")
    utime.sleep_ms(800)
    d_linha(0, "Escaneando...")

    try:
        i0    = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)
        devs0 = i0.scan()
    except Exception:
        devs0 = []

    try:
        i1    = SoftI2C(scl=Pin(15), sda=Pin(14), freq=100000)
        devs1 = i1.scan()
    except Exception:
        devs1 = []

    h0 = ["0x{:02X}".format(d) for d in devs0]
    h1 = ["0x{:02X}".format(d) for d in devs1]

    d_linha(0, "I2C0:" + str(len(devs0)) + " " + (" ".join(h0[:2]) if h0 else "(vazio)"))
    d_linha(1, "")
    d_linha(2, "I2C1:" + str(len(devs1)) + " " + (" ".join(h1[:2]) if h1 else "(vazio)"))
    d_linha(3, "")
    utime.sleep_ms(2000)

    log("  I2C0: " + str(h0))
    log("  I2C1: " + str(h1))

    res = "OK" if 0x3C in devs1 else "FAIL"
    tot = len(devs0) + len(devs1)
    d_resultado(N, res, str(tot) + " dispositivos")
    log_res(N, res, str(tot) + " disp")
    return res

# ------------------------------------------------------------
# 11. LED ONBOARD
# ------------------------------------------------------------
def teste_led_onboard():
    N = "LED ONBOARD"
    log("\n=== " + N + " ===")
    d_header(N, "LED embutido")
    utime.sleep_ms(800)
    d_linha(0, "Piscando 6x...")

    res = "FAIL"
    for pino in ["LED", 25]:
        try:
            led = Pin(pino, Pin.OUT)
            for i in range(6):
                led.value(1)
                d_linha(1, "Estado: ACESO", True)
                utime.sleep_ms(400)
                led.value(0)
                d_linha(1, "Estado: APAGADO")
                utime.sleep_ms(400)
            led.off()
            d_linha(2, "Pino: " + str(pino))
            res = "OK"
            break
        except Exception:
            continue

    d_resultado(N, res, "LED piscou?")
    log_res(N, res)
    return res

# ============================================================
# SEQUENCIA PRINCIPAL
# ============================================================
def executar_testes():
    # Tela de boas-vindas
    oled.fill(0)
    oled.fill_rect(0, 0, 128, 13, 1)
    oled.text("BitDogLab V7", 4, 3, 0)
    oled.text("Teste Hardware", 0, 16, 1)
    oled.text("SDA=GP14 SCL=GP15", 0, 27, 1)
    oled.text("SSD1306 128x64", 0, 37, 1)
    oled.text("Inicio em 3s...", 0, 51, 1)
    oled.show()

    log("\n############################################")
    log("#    TESTE DE HARDWARE - BitDogLab V7     #")
    log("############################################")
    log("Display: SSD1306 | SDA=GP14 | SCL=GP15")
    utime.sleep(3)

    testes = [
        ("Display OLED",  teste_display),
        ("LED RGB",       teste_led_rgb),
        ("Botoes A/B/C",  teste_botoes),
        ("Buzzer",        teste_buzzer),
        ("Neopixel 5x5",  teste_neopixel),
        ("Joystick",      teste_joystick),
        ("Microfone",     teste_microfone),
        ("Chip Interno",  teste_sensores_internos),
        ("Bateria/VSYS",  teste_bateria),
        ("I2C Scan",      teste_i2c_scan),
        ("LED Onboard",   teste_led_onboard),
    ]

    resultados = {}

    for nome, funcao in testes:
        n_atual = len(resultados) + 1
        oled.fill(0)
        oled.fill_rect(0, 0, 128, 13, 1)
        oled.text("PROXIMO TESTE:", 0, 3, 0)
        oled.text(nome[:16], 0, 18, 1)
        oled.text(str(n_atual) + "/" + str(len(testes)), 96, 50, 1)
        d_barra(3, int(n_atual * 100 / len(testes)), "")
        oled.show()
        utime.sleep_ms(1400)

        try:
            resultados[nome] = funcao()
        except Exception as e:
            log("  EXCECAO [" + nome + "]: " + str(e))
            d_resultado(nome, "FAIL", str(e)[:16])
            resultados[nome] = "FAIL"

        utime.sleep_ms(400)

    d_resumo(resultados)

    # Relatorio serial
    log("\n============= RESULTADO FINAL =============")
    for nome, res in resultados.items():
        s = " [OK]  " if res == "OK" else " [FAIL]"
        log(s + " " + nome)
    ok   = sum(1 for v in resultados.values() if v == "OK")
    fail = sum(1 for v in resultados.values() if v == "FAIL")
    log("-------------------------------------------")
    log("  APROVADOS: " + str(ok) +
        "  FALHAS: "    + str(fail) +
        "  TOTAL: "     + str(len(resultados)))
    if fail == 0:
        log("  *** PLACA APROVADA EM TODOS OS TESTES ***")
    else:
        log("  !!! " + str(fail) + " FALHA(S) DETECTADA(S) !!!")
    log("===========================================\n")

# ------------------------------------------------------------
# Ponto de entrada
# Salve como main.py para executar automaticamente ao ligar.
# ------------------------------------------------------------
executar_testes()
