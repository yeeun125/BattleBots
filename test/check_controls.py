"""Compile and exercise the firmware with host-side hardware stubs."""
from pathlib import Path
import subprocess
import tempfile

SOURCE = Path(__file__).resolve().parents[1] / "src/main.cpp"
ARDUINO = r"""
#pragma once
#include <algorithm>
#include <vector>
constexpr int HIGH = 1, LOW = 0, OUTPUT = 1;
int led = LOW;
std::vector<int> delays;
void pinMode(int, int) {}
void digitalWrite(int, int value) { led = value; }
void delay(int ms) { delays.push_back(ms); }
int constrain(int value, int low, int high) { return std::max(low, std::min(value, high)); }
long map(long x, long a, long b, long c, long d) { return (x-a)*(d-c)/(b-a)+c; }
struct SerialStub {
  int pending = -1;
  void begin(int) {}
  bool available() { return pending != -1; }
  int read() { int value = pending; pending = -1; return value; }
} Serial;
"""
SERVO = r"""
#pragma once
#include <vector>
struct Servo {
  int pulse = 0;
  std::vector<int> angles;
  void attach(int, int, int) {}
  void writeMicroseconds(int value) { pulse = value; }
  void write(int value) { angles.push_back(value); }
};
"""
CHECK = r"""
#include <cassert>
void command(char value) { Serial.pending = value; loop(); }
int main() {
  setup();
  const int neutral = BIDIRECTIONAL_ESC ? 1500 : 1000;
  assert(esc.pulse == neutral && currentSpeed == 0);
  assert(delays == std::vector<int>{3000});
  command('w'); assert(currentSpeed == 50 && esc.pulse == (BIDIRECTIONAL_ESC ? 1750 : 1500));
  command('x'); command('+'); assert(currentSpeed == 100 && esc.pulse == 2000);
  command('s'); assert(currentSpeed == 0 && esc.pulse == neutral);
  command('q'); assert(currentSpeed == (BIDIRECTIONAL_ESC ? -40 : 0));
  for (int i = 0; i < 30; ++i) command('-');
  assert(currentSpeed == (BIDIRECTIONAL_ESC ? -100 : 0) && esc.pulse == 1000);
  command('+'); assert(currentSpeed == (BIDIRECTIONAL_ESC ? -90 : 10));
  int speed = currentSpeed;
  command('\n'); command('?'); loop(); assert(currentSpeed == speed);
  command('f');
  assert(flipperServo.angles == (std::vector<int>{0, 120, 0}));
  assert(delays == (std::vector<int>{3000, 300, 400}) && led == LOW);
  command('s'); assert(esc.pulse == neutral);
}
"""
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    (root / "Arduino.h").write_text(ARDUINO)
    (root / "ESP32Servo.h").write_text(SERVO)
    for mode in ("true", "false"):
        source = SOURCE.read_text().replace(
            "BIDIRECTIONAL_ESC = true", f"BIDIRECTIONAL_ESC = {mode}"
        )
        (root / "check.cpp").write_text(source + CHECK)
        binary = root / "check"
        subprocess.run(["c++", "-std=c++11", "-Wall", "-Wextra", "-Werror",
                        "-I", str(root), str(root / "check.cpp"), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
        print(f"PASS: BIDIRECTIONAL_ESC={mode}")
