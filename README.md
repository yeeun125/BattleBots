# BattleBots

ESP32 firmware for a serial-controlled motor ESC and servo flipper, built with Arduino and PlatformIO.

## Overview

This project controls one motor ESC and one flipper servo from single-character USB serial commands. It supports forward/reverse throttle, incremental speed changes, and a timed flipper cycle.

- **Board:** ESP32 Dev Module (`esp32dev`)
- **Framework:** Arduino
- **Build system:** PlatformIO
- **Dependency:** ESP32Servo (`^3.0.9`)

## Hardware and pin assignments

| Component | ESP32 GPIO | Configuration |
| --- | --- | --- |
| Motor ESC signal | 13 | 1000–2000 µs; bidirectional by default |
| Flipper servo signal | 12 | 500–2400 µs; rests at 0°, fires at 120° |
| Status LED | 2 | On during the flipper cycle |

Adjust the pins, ESC pulse limits, and `BIDIRECTIONAL_ESC` in `src/main.cpp` for your hardware. A bidirectional ESC stops at the midpoint (1500 µs); a unidirectional ESC stops at 1000 µs. Startup applies the stop signal and waits three seconds.

## Getting started

Install PlatformIO Core, or the PlatformIO extension for VS Code. Open this project folder, connect the ESP32 over USB, and run:

```sh
# Build the firmware
pio run

# Flash the connected ESP32
pio run --target upload

# Open the serial monitor
pio device monitor --baud 115200
```

The configuration targets the `esp32dev` board and declares ESP32Servo as a dependency.

## Serial controls

Send single characters at 115200 baud. Newlines and unknown characters are ignored.

| Key | Action |
| --- | --- |
| `w` | 50% forward |
| `x` | 100% forward |
| `s` | Stop motor |
| `q` | 40% reverse (bidirectional ESC only) |
| `f` | Fire flipper, then return to rest |
| `+` / `-` | Increase / decrease speed by 10 percentage points |

Speed is clamped to −100…100 in bidirectional mode and 0…100 in unidirectional mode.

## Current limitations

The flipper cycle uses blocking delays (700 ms total), so serial commands are processed after it finishes. There is no communication-loss timeout: the motor retains its last command. These are existing firmware limitations; test with the mechanism secured and an independent way to disconnect power.

## Host-side check

```sh
python3 test/check_controls.py
```

Requires Python 3 and a C++ compiler (`c++`). The check compiles the actual firmware against small Arduino/servo stubs and exercises both ESC modes, speed limits, serial commands, startup, and the flipper sequence. It does not validate ESP32 timing, electrical behavior, or replace a board build and hardware test.

## Project structure

```text
BattleBots/
├── src/main.cpp           # Motor, flipper, and serial command handling
├── test/check_controls.py # Host-side regression check
├── platformio.ini         # Board, framework, and dependency settings
├── .gitignore             # Excludes generated and local files
└── README.md
```

Build caches, editor settings, and backup archives are excluded from version control.
