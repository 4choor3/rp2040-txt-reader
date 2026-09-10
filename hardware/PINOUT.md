# 硬件接线表 (PINOUT) — RP2040 Mini TXT Reader

项目：YD-RP2040 (16MB) + 1.8 寸 ST7735 TFT (128×160, SPI) + 两个翻页按键，运行 CircuitPython 9.x。

---

## 一、屏幕 8 针接线（1.8″ TFT / ST7735）

屏幕采用 SPI 协议，连接到 YD-RP2040 的硬件 SPI1 接口。

| 屏幕引脚 (1.8″ TFT) | 连接至 YD-RP2040 | 物理意义 |
| --- | --- | --- |
| VCC | 3V3 | 屏幕逻辑供电 |
| GND | GND | 信号地 |
| SCL / SCK | GP10 | SPI 硬件时钟 |
| SDA / MOSI | GP11 | SPI 数据输出 |
| RES / RST | GP12 | 屏幕硬件复位 |
| DC / A0 | GP13 | 数据/命令切换线 |
| CS / CE | GP14 | SPI 片选 |
| BLK / LED | 3V3 | 背光供电（常亮） |

> 说明：板上通常只有 1 个 3V3 孔，可将屏幕端 VCC 与 BLK 短接后共用一根飞线接 3V3（屏幕端并联法，最整洁）。

---

## 二、电源链路接线（TP4056 充电保护板 + 锂电池）

供电逻辑：电池 → 充电板 →（拨动开关，可选）→ 主控板。

| 起点引脚 (元件) | 导线连接至 | 终点引脚 (元件) | 状态/说明 |
| --- | --- | --- | --- |
| 电池 红线 (+) | ➔ | TP4056 B+ | 电池充电输入 |
| 电池 黑线 (−) | ➔ | TP4056 B− | 电池接地 |
| TP4056 OUT− | ➔ | YD-RP2040 GND | 系统全局共地 |
| TP4056 OUT+ | ➔ | 拨动开关 引脚 1 | 正极先经开关 |
| 拨动开关 引脚 2 | ➔ | YD-RP2040 Vin (或 5V) | 主板供电输入 |
| TP4056 OUT+ | ➔ | YD-RP2040 Vin (或 5V) | 不加开关时直连（跳过开关） |

> 说明：不加拨动开关也安全，设备会“常开”，电池耗尽时 TP4056 过放保护自动断电。

---

## 三、翻页按键接线

两个微动开关分别用于“上一页 / 下一页”，使用主控板内置上拉电阻，按下时导通到 GND 触发低电平。

| 交互控制 | 按键端 1 | 按键端 2 | 触发逻辑 | 代码引脚 |
| --- | --- | --- | --- | --- |
| 下一页按键 | GP16 | GND | 低电平触发 | `board.GP16` (INPUT_PULLUP) |
| 上一页按键 | GP17 | GND | 低电平触发 | `board.GP17` (INPUT_PULLUP) |

> 接线方式：两个按键各自一端并联接到 GND，另一端分别接 GP16 / GP17。代码中开启 `digitalio.Pull.UP`，按下即拉低。

---

## 四、CIRCUITPY 盘期望目录结构

将 YD-RP2040 刷入 CircuitPython 9.x 后，电脑上会出现名为 `CIRCUITPY` 的 U 盘。文件层级必须如下（库文件层级错误会导致静默失败）：

```
CIRCUITPY/
├── code.py                        # 主程序 (TXT 阅读器), 见仓库根目录
├── book.txt                       # 要阅读的 UTF-8 文本 (自行放入)
├── font.bdf                       # 中文位图字体 (bitmap_font.load_font 加载)
├── image.bmp                      # 示例图片 (examples/image_viewer.py 使用, 可选)
└── lib/
    ├── adafruit_st7735r.mpy       # 屏幕底层驱动 (单个 .mpy 文件)
    └── adafruit_display_text/     # 文本排版与渲染库 (整个文件夹)
        ├── __init__.mpy
        ├── label.mpy
        ├── bitmap_label.mpy
        ├── outlined_label.mpy
        ├── scrolling_label.mpy
        └── text_box.mpy
```

> 复制库文件（macOS 示例）：
> ```sh
> cp -r adafruit_st7735r.mpy /Volumes/CIRCUITPY/lib/
> cp -r adafruit_display_text /Volumes/CIRCUITPY/lib/
> ```

---

## 五、关键注意事项

- **CircuitPython 9.x 语法**：显示总线必须用 `import fourwire` + `fourwire.FourWire(...)`，旧版 `displayio.FourWire(...)` 在 9.x 中已移除（会报 `AttributeError: module 'displayio' has no attribute 'FourWire'`）。
- **图片格式**：`OnDiskBitmap` 仅支持标准 **24 位 BMP**，分辨率严格 128×160，不支持 JPG/PNG/32 位 BMP。
- **屏幕变体**：绝大多数 1.8″ 屏为 ST7735/ST7735R/ST7735S；若为 ST7789 需换对应驱动库。
