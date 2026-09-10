"""
pi_2000.py - ST7735 TFT 上滚动输出 2000 位圆周率
====================================================

用途:
    利用 Python 无限精度整数, 在 RP2040 上实时运行 Spigot 算法计算 π,
    并以终端风格在 1.8 寸 TFT 屏幕上绿字滚动输出, 直到 2000 位后暂停 3 秒
    清屏, 再循环重新开始。

硬件平台: YD-RP2040 (16MB) + 1.8 寸 ST7735 TFT (128x160, SPI)
运行环境: CircuitPython 9.x

依赖库:
    - adafruit_st7735r  (屏幕底层驱动)
    - adafruit_display_text (label 文本标签)

引脚约定:
    SPI: clock=GP10, MOSI=GP11
    TFT: reset=GP12, dc=GP13, cs=GP14

重要 (CircuitPython 9.x):
    必须使用 `import fourwire` + `fourwire.FourWire(...)`.

显示参数:
    字体: terminalio.FONT (内置, 无需外部字体文件, 仅含 ASCII/数字)
    颜色: 0x00FF00 (亮绿)
    滚动窗口: 14 行 x 21 字符 (128 宽约 21 个 6px 字符; 160 高约 14 行)

使用方法:
    1. 将 adafruit_st7735r.mpy 与 adafruit_display_text/ 放入 CIRCUITPY/lib/
    2. 本文件覆盖到 CIRCUITPY/code.py 保存运行
    3. 屏幕开始逐位输出绿色 π 数字; 满 2000 位暂停 3 秒后自动清屏循环

注意:
    随着位数增加, Spigot 算法的大整数运算量上升, 数字滚动会逐渐变慢,
    这是正常现象 (芯片算力限制), 非程序错误。
"""

import board
import busio
import displayio
import fourwire  # CircuitPython 9.x: FourWire 独立成 fourwire 模块
import terminalio
import time

from adafruit_st7735r import ST7735R
from adafruit_display_text import label

displayio.release_displays()

# 硬件 SPI 总线
spi = busio.SPI(clock=board.GP10, MOSI=board.GP11)

# 显示总线 (CircuitPython 9.x 语法)
display_bus = fourwire.FourWire(
    spi, command=board.GP13, chip_select=board.GP14, reset=board.GP12
)

# ST7735R 屏幕对象
display = ST7735R(display_bus, width=128, height=160, bgr=True)

# 文本图层: 绿字, 终端风格
text_area = label.Label(terminalio.FONT, text="", color=0x00FF00, line_spacing=1.0)
text_area.x = 2
text_area.y = 4
group = displayio.Group()
group.append(text_area)
display.root_group = group


def generate_pi():
    """
    Spigot 算法生成圆周率每一位数字 (无限迭代器).
    利用 Python 的任意精度整数, 无需外部文件即可逐位产出 π 的数字。
    """
    q, r, t, k, n, l = 1, 0, 1, 1, 3, 3
    while True:
        if 4 * q + r - t < n * t:
            yield str(n)
            q, r, t, k, n, l = (10 * q, 10 * (r - n * t), t, k,
                                (10 * (3 * q + r)) // t - 10 * n, l)
        else:
            q, r, t, k, n, l = (q * k, (2 * q + r) * l, t * l, k + 1,
                                (q * (7 * k + 2) + r * l) // (t * l), l + 2)


# 滚动窗口尺寸
MAX_LINES = 14
CHARS_PER_LINE = 21

while True:
    # 新一轮计算
    pi_gen = generate_pi()
    next(pi_gen)  # 跳过首位的 "3", 由下面的 "3." 手动显示

    lines = ["3."]
    digit_count = 0

    while digit_count < 2000:
        digit = next(pi_gen)
        digit_count += 1

        # 当前行未满则追加, 否则换行; 超过窗口行数则移除最旧的一行
        if len(lines[-1]) < CHARS_PER_LINE:
            lines[-1] += digit
        else:
            lines.append(digit)
            if len(lines) > MAX_LINES:
                lines.pop(0)

        text_area.text = "\n".join(lines)

    # 输出满 2000 位, 暂停 3 秒后清屏, 下一轮 while 自动重新计算循环
    time.sleep(3)
    text_area.text = ""
