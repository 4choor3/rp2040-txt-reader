# RP2040 Mini TXT Reader

> A ultra-low-cost, pocket-sized DIY TXT e-book reader built on the **YD-RP2040** (16MB) microcontroller and a **1.8" ST7735 TFT** screen, running on **CircuitPython 9.x**.

[![CircuitPython](https://img.shields.io/badge/CircuitPython-9.x-4d2d8f)](https://circuitpython.org/)
[![Cost](https://img.shields.io/badge/cost-%3C%20%C2%A530-brightgreen)](https://github.com/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Once flashed, the board shows up as a USB **Mass Storage** (U-disk). Dropping a UTF-8 `book.txt` onto it is all you need to load a new book — no compiler, no Wi-Fi, no re-flashing. Just press the page buttons to read.

## ✨ Features

- **U-disk style book loading** — CircuitPython maps the on-board 16MB flash to a USB drive; copy `book.txt` like a normal file.
- **Ultra-low cost** — total bill of materials stays under ¥30 (≈ $4) using commodity modules.
- **Pocket "sandwich" form factor** — screen → buffer layer → battery → MCU stacked into a matchbox-sized slab.
- **Full Chinese text rendering** — pixel `.bdf` font + `adafruit_bitmap_font` for crisp monochrome-style output on a color LCD.
- **Battery powered** — 3.7V Li-Po + TP4056 charge/protect board; optional slide switch for hard power-off.
- **Two physical page buttons** — previous / next page with on-board pull-ups.

## 🧰 Hardware List

| Component | Model / Spec | Notes |
|-----------|--------------|-------|
| Main MCU | **YD-RP2040** 16MB Flash | 53.3 × 22.9 mm, Type-C, made by VCC-GND Studio. Order the **un-soldered (no header)** version. |
| Display | **1.8" TFT LCD** (ST7735 driver) | 128×160, SPI, 8-pin module **with a PCB carrier board** (not a bare FPC screen). |
| Battery | **503035** Li-Po | ~500–600 mAh, 3.7V, flat pack that fits behind the screen. |
| Charge/Protect | **TP4056** Type-C module | Handles Li-Po charging & over-discharge protection. |
| Page buttons | Tactile micro switch × 2 | For "next page" / "prev page". |
| Power switch | **SS12d00** slide switch × 1 (optional) | Hard power cut between TP4056 and MCU. |
| Wiring | 30AWG silicone wire | For thin fly-wiring in tight spaces. |

## 🔌 Wiring

**Power chain:** Battery → TP4056 → (slide switch) → YD-RP2040

| From (component) | To (YD-RP2040) | Function |
|------------------|----------------|----------|
| Battery red (+) | TP4056 **B+** | Battery charge input |
| Battery black (−) | TP4056 **B−** | Battery ground |
| TP4056 **OUT−** | **GND** | Common ground |
| TP4056 **OUT+** | Slide switch pin 1 | Positive output (intercepted by switch) |
| Slide switch pin 2 | **Vin** | MCU power input (or connect OUT+ → Vin directly if switch omitted) |
| Screen **VCC / BLK** | **3V3** | Screen logic + backlight (join VCC & BLK at screen side) |
| Screen **GND** | **GND** | Ground |
| Screen **SCL** (SCK) | **GP10** | SPI clock |
| Screen **SDA** (MOSI) | **GP11** | SPI data |
| Screen **RES** (RST) | **GP12** | Reset |
| Screen **DC** (A0) | **GP13** | Data/command select |
| Screen **CS** (CE) | **GP14** | SPI chip select |
| Next-page button | **GP16** + GND | Next page (internal pull-up) |
| Prev-page button | **GP17** + GND | Previous page (internal pull-up) |

> **Note:** The YD-RP2040 has only one **3V3** pin. Join the screen's **VCC** and **BLK** at the screen side, then run a single wire to **3V3**.

## 📦 Software Dependencies

Runs under **CircuitPython 9.x**. Place these in the `lib/` folder of the `CIRCUITPY` drive:

1. **`adafruit_st7735r.mpy`** — low-level ST7735R screen driver.
2. **`adafruit_display_text/`** — text layout & rendering library (folder, not a single file).

For Chinese TXT rendering you also need a pixel font: **`font.bdf`** (a Chinese-capable `.bdf` bitmap font) placed in the drive root, loaded via `adafruit_bitmap_font`.

> **Gotcha — CircuitPython 9.x:** `displayio.FourWire` was moved out of `displayio` into its own module. You must `import fourwire` and call `fourwire.FourWire(...)`. (On 8.x it was `displayio.FourWire`.)

## 🚀 Quick Start

1. **Flash CircuitPython 9.x firmware**
   - Hold **BOOT**, plug in Type-C, release BOOT → an `RPI-RP2` drive appears.
   - Drag the Raspberry Pi Pico / YD-RP2040 `.uf2` into it. It reboots as `CIRCUITPY`.

2. **Install dependencies** (macOS example):
   ```sh
   cp adafruit_st7735r.mpy /Volumes/CIRCUITPY/lib/
   cp -r adafruit_display_text /Volumes/CIRCUITPY/lib/
   ```

3. **Add the font & book:**
   ```sh
   cp font.bdf            /Volumes/CIRCUITPY/
   cp book.txt            /Volumes/CIRCUITPY/   # UTF-8 encoded TXT
   ```

4. **Write `code.py`** to the drive root (see `examples/`). Saving auto-runs the code.

## 📁 Project Structure

```
rp2040-txt-reader/
├── README.md                  # This file (English)
├── code.py                    # Main reader firmware (CircuitPython 9.x)
├── LICENSE                    # MIT License
├── docs/
│   └── BUILD_GUIDE.zh-CN.md   # Full Chinese build guide
├── examples/
│   ├── color_test.py          # Solid-red hardware test
│   ├── image_viewer.py        # Display /image.bmp (24-bit, 128x160)
│   └── pi_2000.py             # Spigot algorithm rolling π demo
└── hardware/
    └── PINOUT.md              # Full pin mapping & drive layout
```

A minimal `code.py` skeleton (CP 9.x syntax):

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

## 📖 Story (How this project came to be)

This reader went through a long hardware-selection and debugging journey — captured here so you don't repeat the mistakes.

1. **Plan A — ESP32 + TFT/OLED.** Started with the classic ESP32 + TFT LCD over SPI, using Arduino + `TFT_eSPI`, uploading TXT via `ESP32 Sketch Data Upload` or a Wi-Fi web server. Powerful, but needs a compiler and Wi-Fi for book transfer.
2. **Plan B — ESP32-C3 SuperMini (≈¥25).** A coin-sized board acting as its own Wi-Fi AP; phone uploads TXT through a web page. Cheap and wireless, but still needs Wi-Fi and the Arduino toolchain.
3. **Plan C — ESP32 16MB + I2C OLED.** Chased the "16MB + monochrome" requirement with a 1.3" OLED and the `U8g2` Chinese font. Good contrast, but the screen is tiny and the firmware build is heavy.
4. **Plan D — RP2040 U-disk style (chosen).** Dropped Wi-Fi entirely. The YD-RP2040 with **native USB MSC** turns into a U-disk under CircuitPython: edit code and drop TXT by copy-paste, no re-flashing. Around ¥9–11 for the MCU.
5. **Screen selection.** A 1.8" ST7735 TFT (128×160) was picked over OLED/dot-matrix for the best price-per-character — set text to white (`0xFFFFFF`) on black (`0x000000`) to use it as a high-res monochrome reader.
6. **Sizing & battery.** The 53.3×22.9 mm board hides perfectly behind the ~56×34 mm screen. A **503035** Li-Po + **TP4056** charge/protect board gives portable power.
7. **Selection fixes.** Swapped a bare FPC screen (0.5mm pitch, un-solderable by hand) for an **8-pin module with PCB底板**; requested the **un-soldered** YD-RP2040 so the sandwich stays thin.
8. **Assembly tricks.** Screen back has raised components → built an **EVA foam "wall"** + a hard plastic sheet as a puncture-proof buffer; removed headers with a soldering iron + tweezers; single **3V3** pin → join VCC/BLK at the screen side.
9. **Debugging.** White backlight but no image → fixed `AttributeError: module has no attribute 'FourWire'` by switching to `import fourwire` (CP 9.x change). Missing `adafruit_display_text` → copied via `cp -r` in the macOS terminal.

## 📄 License

Released under the [MIT License](LICENSE). Copyright (c) 2026 Chen Xinyu.
