"""
RP2040 Mini TXT Reader - 主程序 (TXT 阅读器)
=============================================

硬件平台:
    YD-RP2040 (16MB 闪存) + 1.8 寸 ST7735 TFT (128x160, SPI) + 两个翻页按键
    运行环境: CircuitPython 9.x

文件结构 (CIRCUITPY 根目录):
    code.py                  <- 本文件
    book.txt                 <- 要阅读的 UTF-8 文本 (自行放入)
    font.bdf                 <- 中文位图字体 (bitmap_font.load_font 加载)
    lib/
        adafruit_st7735r.mpy      <- 屏幕底层驱动
        adafruit_display_text/    <- 文本排版与渲染库

依赖库:
    - adafruit_st7735r  (屏幕驱动)
    - adafruit_display_text (label 文本标签)
    - adafruit_bitmap_font (bitmap_font 加载 .bdf 字体)

引脚约定 (见 hardware/PINOUT.md):
    SPI: clock=GP10, MOSI=GP11
    TFT: reset=GP12, dc=GP13, cs=GP14
    下页按键: GP16, 上页按键: GP17  (INPUT_PULLUP, 接 GND 低电平触发)

注意 (CircuitPython 9.x):
    必须使用 `import fourwire` + `fourwire.FourWire(...)`，
    不要再使用 displayio.FourWire (8.x 旧语法)。

功能说明:
    - 每屏约读取 110 个字符 (128x160 / 12px 中文字体的合理容量)
    - 翻页采用"按当前屏实际显示字符数回退"逻辑:
        下一页: 从当前文件位置继续读取下一段
        上一页: 回退量 = 本页实际显示字符数 * 2 (回到本页起点之前再往前一屏)
    - 按键防抖使用 time.monotonic() (非 sleep 阻塞)
    - book.txt 不存在时屏幕提示错误
"""

import board
import busio
import digitalio
import displayio
import time
import fourwire  # CircuitPython 9.x: FourWire 已移出 displayio, 独立成 fourwire 模块

from adafruit_st7735r import ST7735R
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

# ---------------------------------------------------------------------------
# 硬件初始化
# ---------------------------------------------------------------------------
displayio.release_displays()

# SPI 总线 (硬件 SPI1): clock=GP10, MOSI=GP11
spi = busio.SPI(clock=board.GP10, MOSI=board.GP11)

# 屏幕控制引脚
tft_cs = board.GP14
tft_dc = board.GP13
tft_reset = board.GP12

# 显示总线 (CircuitPython 9.x 语法)
display_bus = fourwire.FourWire(
    spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset
)

# ST7735R 屏幕对象 (bgr=True: 该模块颜色顺序为 BGR)
display = ST7735R(display_bus, width=128, height=160, bgr=True)

# 翻页按键: INPUT_PULLUP, 按下时拉低到 GND 触发
btn_next = digitalio.DigitalInOut(board.GP16)  # 下一页
btn_next.direction = digitalio.Direction.INPUT
btn_next.pull = digitalio.Pull.UP

btn_prev = digitalio.DigitalInOut(board.GP17)  # 上一页
btn_prev.direction = digitalio.Direction.INPUT
btn_prev.pull = digitalio.Pull.UP

# ---------------------------------------------------------------------------
# 文本图层
# ---------------------------------------------------------------------------
# 加载中文位图字体 (需自行提供 font.bdf 放到 CIRCUITPY 根目录)
try:
    font = bitmap_font.load_font("/font.bdf")
except Exception as exc:  # 字体缺失时给出明确提示而非静默崩溃
    # 用内置 terminalio 字体显示错误 (terminalio 无需外部字体文件)
    import terminalio

    text_area = label.Label(
        terminalio.FONT,
        text="字体 font.bdf 缺失\n请放入 CIRCUITPY 根目录",
        color=0xFF0000,
        x=0,
        y=8,
    )
    group = displayio.Group()
    group.append(text_area)
    display.root_group = group
    raise SystemExit("加载 font.bdf 失败: %s" % exc)

text_area = label.Label(font, text=" 系统初始化中 ...", color=0xFFFFFF, x=0, y=8)
text_group = displayio.Group()
text_group.append(text_area)
display.root_group = text_group

# ---------------------------------------------------------------------------
# 常量与状态
# ---------------------------------------------------------------------------
BOOK_PATH = "/book.txt"
CHARS_PER_SCREEN = 110  # 每屏读取的字符数 (12px 中文字体在 128x160 下的合理容量)

# 按键防抖: 记录上次触发时间, 两次触发间隔需 > DEBOUNCE_MS
DEBOUNCE_S = 0.2
last_press = {"next": 0.0, "prev": 0.0}

# 当前文件读取位置
current_pos = 0
# 本页实际显示的字符数 (供"上一页"回退计算使用)
shown_chars = 0


# ---------------------------------------------------------------------------
# 功能函数
# ---------------------------------------------------------------------------
def show_error(message):
    """在屏幕上显示错误信息 (红字), 不退出循环."""
    text_area.color = 0xFF0000
    text_area.text = message
    display.root_group = text_group


def read_forward(file_pointer):
    """
    读取下一屏文本.

    从 file_pointer 位置开始读取最多 CHARS_PER_SCREEN 个字符,
    返回 (显示内容, 实际显示字符数, 新的文件位置).
    当到达文件末尾时, 末尾之后的新位置等于旧位置 (不会再前进).
    """
    try:
        with open(BOOK_PATH, "r", encoding="utf-8") as f:
            f.seek(file_pointer)
            content = f.read(CHARS_PER_SCREEN)
            new_pos = f.tell()
    except OSError:
        return None, 0, file_pointer

    return content, len(content), new_pos


def read_page_from(file_pointer):
    """
    从指定位置读取一屏并显示.

    返回 (实际显示字符数, 新的文件位置).
    若 book.txt 不存在, 显示错误并返回 (0, 0).
    """
    global shown_chars
    content, shown, new_pos = read_forward(file_pointer)
    if content is None:
        show_error("未找到 book.txt\n请放入 CIRCUITPY 根目录")
        shown_chars = 0
        return 0, 0

    text_area.color = 0xFFFFFF
    text_area.text = content
    display.root_group = text_group
    shown_chars = shown
    return shown, new_pos


def go_next():
    """下一页: 从当前位置继续读下一段."""
    global current_pos
    _, current_pos = read_page_from(current_pos)


def go_prev():
    """
    上一页: 回退量 = 本页实际显示字符数 * 2.

    逻辑说明:
        本页起点 = current_pos - shown_chars (本页实际显示的字符数).
        再往前一整屏 = 本页起点 - shown_chars = current_pos - shown_chars*2.
        取 max(0, ...) 防止越过文件开头.
    """
    global current_pos
    target = max(0, current_pos - shown_chars * 2)
    _, current_pos = read_page_from(target)


def button_pressed(btn, key):
    """带防抖的按键检测: 返回 True 表示这次应触发."""
    global last_press
    if not btn.value:  # 低电平 = 按下
        now = time.monotonic()
        if now - last_press[key] > DEBOUNCE_S:
            last_press[key] = now
            return True
    return False


# ---------------------------------------------------------------------------
# 主循环
# ---------------------------------------------------------------------------
# 首屏
_, current_pos = read_page_from(0)

while True:
    if button_pressed(btn_next, "next"):
        go_next()

    if button_pressed(btn_prev, "prev"):
        go_prev()
