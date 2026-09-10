"""
color_test.py - ST7735 TFT 纯色硬件测试 (红屏)
===============================================

用途:
    验证 YD-RP2040 与 1.8 寸 ST7735 TFT 屏幕的接线与通信是否正常。
    代码不读取任何外部文件, 直接命令屏幕显示纯红色, 用于硬件排障。

硬件平台: YD-RP2040 (16MB) + 1.8 寸 ST7735 TFT (128x160, SPI)
运行环境: CircuitPython 9.x

依赖库:
    - adafruit_st7735r  (屏幕底层驱动)

引脚约定:
    SPI: clock=GP10, MOSI=GP11
    TFT: reset=GP12, dc=GP13, cs=GP14

重要 (CircuitPython 9.x):
    必须使用 `import fourwire` + `fourwire.FourWire(...)`,
    8.x 旧语法 `displayio.FourWire(...)` 在 9.x 中已移除。

使用方法:
    1. 将 adafruit_st7735r.mpy 放入 CIRCUITPY/lib/
    2. 把本文件内容覆盖到 CIRCUITPY/code.py
    3. 保存后屏幕应变红:
       - 纯红  -> 接线与通信正常, 故障在其它地方 (如图片格式)
       - 仍白光 -> 数据线虚焊/接错 (查 GP10~GP14)
       - 彩色雪花 -> 驱动初始化偏移问题 (尝试调整 bgr 或加偏移量)

可修改 color_palette[0] 更换测试颜色, 例如:
    0x00FF00 绿, 0x0000FF 蓝, 0xFFFFFF 白
"""

import board
import busio
import displayio
import fourwire  # CircuitPython 9.x: FourWire 独立成 fourwire 模块

from adafruit_st7735r import ST7735R

displayio.release_displays()

# 硬件 SPI 总线
spi = busio.SPI(clock=board.GP10, MOSI=board.GP11)

# 显示总线 (CircuitPython 9.x 语法)
display_bus = fourwire.FourWire(
    spi, command=board.GP13, chip_select=board.GP14, reset=board.GP12
)

# ST7735R 屏幕对象
display = ST7735R(display_bus, width=128, height=160, bgr=True)

# 创建 128x160 单色位图与调色板
color_bitmap = displayio.Bitmap(128, 160, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFF0000  # 纯红 (测试色)

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
group = displayio.Group()
group.append(bg_sprite)
display.root_group = group

while True:
    pass
