# RP2040 Mini TXT Reader

> 基于 **YD-RP2040**（16MB）微控制器与 **1.8 寸 ST7735 TFT** 屏幕的超低成本、口袋尺寸 DIY TXT 电子书阅读器，运行于 **CircuitPython 9.x**。

[![CircuitPython](https://img.shields.io/badge/CircuitPython-9.x-4d2d8f)](https://circuitpython.org/)
[![成本](https://img.shields.io/badge/成本-低于%2030%20元-brightgreen)](https://github.com/4choor3/rp2040-txt-reader)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

烧录固件后，板子会以 **U 盘** 形式出现在电脑上。换书只需把 UTF-8 编码的 `book.txt` 拖进去——无需编译器、无需 Wi-Fi、无需重新烧录，按下翻页按键即可阅读。

## ✨ 特性

- **U 盘式传书** — CircuitPython 将板载 16MB 闪存映射为 USB 磁盘，像拷贝普通文件一样放入 `book.txt`。
- **超低成本** — 全部物料合计低于 ¥30（约 $4），全部使用市面通用模块。
- **口袋「三明治」结构** — 屏幕 → 缓冲层 → 电池 → 主控板层叠，火柴盒大小的平板形态。
- **完整中文渲染** — 像素 `.bdf` 字体 + `adafruit_bitmap_font`，在彩屏上实现清晰的黑底白字效果。
- **电池供电** — 3.7V 锂聚合物电池 + TP4056 充放电保护板，可选拨动开关硬断电。
- **两个物理翻页按键** — 上页 / 下页，使用板载上拉电阻。

## 🧰 硬件清单

| 部件 | 型号 / 规格 | 说明 |
|------|-------------|------|
| 主控板 | **YD-RP2040** 16MB 闪存版 | 53.3 × 22.9 mm，Type-C，VCC-GND Studio 出品。务必购买**未焊接排针（散件）**版本。 |
| 显示屏 | **1.8 寸 TFT LCD**（ST7735 驱动） | 128×160，SPI 接口，8 针**带 PCB 底板**模块（不要买裸屏 FPC 排线版）。 |
| 电池 | **503035** 聚合物锂电池 | 约 500–600 mAh，3.7V，扁平外形正好藏在屏幕背后。 |
| 充放电板 | **TP4056** Type-C 模块 | 负责锂电池充电与过放保护。 |
| 翻页按键 | 轻触微动开关 × 2 | 分别实现「上一页」「下一页」。 |
| 电源开关 | **SS12d00** 拨动开关 × 1（可选） | 串联在 TP4056 与主控板之间，硬断电。 |
| 导线 | 30AWG 硅胶软线 | 狭小空间内飞线焊接。 |

## 🔌 接线方案

**电源链路：** 电池 → TP4056 →（拨动开关）→ YD-RP2040

| 起点（元件） | 终点（YD-RP2040） | 功能 |
|--------------|-------------------|------|
| 电池红线 (+) | TP4056 **B+** | 电池充电输入 |
| 电池黑线 (−) | TP4056 **B−** | 电池接地 |
| TP4056 **OUT−** | **GND** | 全局共地 |
| TP4056 **OUT+** | 拨动开关引脚 1 | 正极输出（经开关拦截） |
| 拨动开关引脚 2 | **Vin** | 主控板供电输入（不加开关时 OUT+ 直连 Vin） |
| 屏幕 **VCC / BLK** | **3V3** | 屏幕逻辑 + 背光供电（屏幕端把 VCC 与 BLK 并联） |
| 屏幕 **GND** | **GND** | 接地 |
| 屏幕 **SCL** (SCK) | **GP10** | SPI 时钟 |
| 屏幕 **SDA** (MOSI) | **GP11** | SPI 数据 |
| 屏幕 **RES** (RST) | **GP12** | 复位 |
| 屏幕 **DC** (A0) | **GP13** | 数据/命令切换 |
| 屏幕 **CS** (CE) | **GP14** | SPI 片选 |
| 下页按键 | **GP16** + GND | 下一页（内部上拉） |
| 上页按键 | **GP17** + GND | 上一页（内部上拉） |

> **注意：** YD-RP2040 板上通常只有一个 **3V3** 孔。将屏幕的 **VCC** 与 **BLK** 在屏幕端短接并联，只引一根线接到 **3V3** 即可。

## 📦 软件依赖

运行于 **CircuitPython 9.x**。以下库需放入 `CIRCUITPY` 盘的 `lib/` 目录：

1. **`adafruit_st7735r.mpy`** — ST7735R 屏幕底层驱动。
2. **`adafruit_display_text/`** — 文本排版与渲染库（是文件夹，不是单文件）。

中文 TXT 渲染还需要像素字体：**`font.bdf`**（支持中文的 `.bdf` 位图字体），放在磁盘根目录，通过 `adafruit_bitmap_font` 加载。

> **坑点 — CircuitPython 9.x：** `displayio.FourWire` 已从 `displayio` 中独立出来。必须 `import fourwire` 并调用 `fourwire.FourWire(...)`。（8.x 旧版才是 `displayio.FourWire`。）

## 🚀 快速开始

1. **烧录 CircuitPython 9.x 固件**
   - 按住 **BOOT**，插入 Type-C 数据线，松开 BOOT → 电脑出现 `RPI-RP2` 盘。
   - 将 Raspberry Pi Pico / YD-RP2040 对应的 `.uf2` 固件拖入其中，板子自动重启为 `CIRCUITPY` 盘。

2. **安装依赖库**（macOS 示例）：
   ```sh
   cp adafruit_st7735r.mpy /Volumes/CIRCUITPY/lib/
   cp -r adafruit_display_text /Volumes/CIRCUITPY/lib/
   ```

3. **放入字体与小说：**
   ```sh
   cp font.bdf /Volumes/CIRCUITPY/
   cp book.txt /Volumes/CIRCUITPY/   # UTF-8 编码的 TXT 文件
   ```

4. **写入 `code.py`**（本仓库根目录的主程序）到磁盘根目录。保存瞬间自动运行。演示脚本见 `examples/`。

## 📁 项目结构

```
rp2040-txt-reader/
├── README.md                  # 本文件
├── code.py                    # 主程序：TXT 阅读器固件（CircuitPython 9.x）
├── LICENSE                    # MIT License
├── docs/
│   └── BUILD_GUIDE.zh-CN.md   # 完整中文制作指南
├── examples/
│   ├── color_test.py          # 纯红屏硬件测试
│   ├── image_viewer.py        # 显示 /image.bmp（24 位 128x160）
│   └── pi_2000.py             # Spigot 算法滚动输出 2000 位圆周率
└── hardware/
    └── PINOUT.md              # 完整引脚接线表与磁盘目录结构
```

一个最小化的 `code.py` 骨架（CP 9.x 语法）：

```python
import board, busio, displayio, fourwire, time
from adafruit_st7735r import ST7735R
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

displayio.release_displays()
spi = busio.SPI(clock=board.GP10, MOSI=board.GP11)
display_bus = fourwire.FourWire(
    spi, command=board.GP13, chip_select=board.GP14, reset=board.GP12)
display = ST7735R(display_bus, width=128, height=160, bgr=True)

btn_next = digitalio.DigitalInOut(board.GP16)
btn_next.direction = digitalio.Direction.INPUT
btn_next.pull = digitalio.Pull.UP
btn_prev = digitalio.DigitalInOut(board.GP17)
btn_prev.direction = digitalio.Direction.INPUT
btn_prev.pull = digitalio.Pull.UP

font = bitmap_font.load_font("/font.bdf")
text_group = displayio.Group()
text_area = label.Label(font, text=" 系统初始化中 ...", color=0xFFFFFF, x=0, y=8)
text_group.append(text_area)
display.root_group = text_group

def read_page(pos):
    with open("/book.txt", "r", encoding="utf-8") as f:
        f.seek(pos)
        text_area.text = f.read(110)
        return f.tell()

current_pos = read_page(0)
while True:
    if not btn_next.value:
        time.sleep(0.2); current_pos = read_page(current_pos)
    if not btn_prev.value:
        time.sleep(0.2)
        current_pos = max(0, current_pos - 220)
        current_pos = read_page(current_pos)
```

## 📖 项目历程

这台阅读器经历了漫长的选型与调试之路，记录在此，帮你避开重复踩过的坑。

1. **方案 A — ESP32 + TFT/OLED。** 最初的经典路线：ESP32 + SPI TFT，Arduino + `TFT_eSPI` 开发，通过 `ESP32 Sketch Data Upload` 插件或局域网网页服务器传书。性能强，但每次传书都要编译环境和 Wi-Fi。
2. **方案 B — ESP32-C3 SuperMini（约 ¥25）。** 硬币大小的板子自己发射 Wi-Fi 热点，手机连热点后经网页上传 TXT。便宜且无线，但仍依赖 Wi-Fi 和 Arduino 工具链。
3. **方案 C — ESP32 16MB + I2C OLED。** 为满足「16MB + 黑白屏」需求，用 1.3 寸 OLED + `U8g2` 中文字库。对比度高，但屏幕太小、固件构建繁重。
4. **方案 D — RP2040 U 盘式（最终选定）。** 彻底抛弃 Wi-Fi。YD-RP2040 原生 USB MSC，刷入 CircuitPython 后直接变 U 盘：改代码、放 TXT 全部复制粘贴，免重新烧录。主控约 ¥9–11。
5. **屏幕选择。** 最终选 1.8 寸 ST7735 TFT（128×160）——单字成本最优。代码中把文字设白（`0xFFFFFF`）背景设黑（`0x000000`），当作高分辨率单色屏使用。
6. **尺寸与供电。** 53.3×22.9 mm 的主控板正好藏在约 56×34 mm 的屏幕背后；**503035** 锂电池 + **TP4056** 充放电板提供便携供电。
7. **选型纠错。** 裸屏 FPC 排线（0.5mm 间距）手工无法焊接 → 换成 **8 针带 PCB 底板**模块；要求发**未焊接排针**的 YD-RP2040，保证三明治结构足够薄。
8. **组装工艺。** 屏幕背面元件凸起 → 用 **EVA 海绵胶贴出边缘「围墙」** + 硬塑料片做防刺穿层；电烙铁 + 镊子拆除排针；单 **3V3** 孔 → 屏幕端 VCC/BLK 并联。
9. **调试排障。** 背光亮但无图像 → `AttributeError: module has no attribute 'FourWire'` 切换为 `import fourwire`（CP 9.x 变更）解决；缺 `adafruit_display_text` 库 → macOS 终端 `cp -r` 解决。

## 📄 License

采用 [MIT License](LICENSE)。Copyright (c) 2026 Chen Xinyu.
