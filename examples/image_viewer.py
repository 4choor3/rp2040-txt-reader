"""
image_viewer.py - 在 ST7735 TFT 上显示 BMP 图片
================================================

用途:
    从 CIRCUITPY 根目录读取 /image.bmp 并在 1.8 寸 TFT 屏幕上全屏显示。
    可作为图片查看/开机画面演示。

硬件平台: YD-RP2040 (16MB) + 1.8 寸 ST7735 TFT (128x160, SPI)
运行环境: CircuitPython 9.x

依赖库:
    - adafruit_st7735r  (屏幕底层驱动)

引脚约定:
    SPI: clock=GP10, MOSI=GP11
    TFT: reset=GP12, dc=GP13, cs=GP14

重要 (CircuitPython 9.x):
    必须使用 `import fourwire` + `fourwire.FourWire(...)`.

图片格式要求 (关键!):
    CircuitPython 的 displayio.OnDiskBitmap 对 BMP 要求非常严格:
    1. 分辨率必须严格为 128 x 160 (与屏幕一致)
    2. 必须是标准 24 位 BMP (24-bit / 像素), 不可带压缩
    3. 不支持 JPG / PNG (MCU 内存不足以解压)
    4. 不支持 32 位带 Alpha 通道的 BMP

推荐用 Windows 画图转换:
    打开图片 -> 重新调整大小 128x160 -> 文件 -> 另存为 -> BMP 图片
    -> 保存类型务必选 "24位位图 (*.bmp;*.dib)"
    -> 重命名为 image.bmp 放入 CIRCUITPY 根目录

使用方法:
    1. 将 adafruit_st7735r.mpy 放入 CIRCUITPY/lib/
    2. 准备 image.bmp (见上方格式要求) 放入 CIRCUITPY 根目录
    3. 本文件覆盖到 CIRCUITPY/code.py 保存运行
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

# 打开并解码 BMP (OnDiskBitmap 流式解码, 不占大块 RAM)
image_file = open("/image.bmp", "rb")
bitmap = displayio.OnDiskBitmap(image_file)

# 用位图自身的像素着色器映射到 TileGrid
tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
group = displayio.Group()
group.append(tile_grid)
display.root_group = group

# 图片静态显示, 主循环空转
while True:
    pass
