#include <Arduino.h>
#include <ESP32Servo.h>

constexpr int ESC_PIN = 13;
constexpr int SERVO_PIN = 12;
constexpr int LED_PIN = 2;

Servo esc;
Servo flipperServo;

constexpr int ESC_MIN_US = 1000;
constexpr int ESC_MAX_US = 2000;
constexpr bool BIDIRECTIONAL_ESC = true;

int currentSpeed = 0;

void setMotorSpeed(int speed) {
  const int minimumSpeed = BIDIRECTIONAL_ESC ? -100 : 0;
  currentSpeed = constrain(speed, minimumSpeed, 100);
  const int pulse = map(currentSpeed, minimumSpeed, 100, ESC_MIN_US, ESC_MAX_US);

  esc.writeMicroseconds(pulse);
}

void stopMotor() {
  setMotorSpeed(0);
}

void fireFlipper() {
  digitalWrite(LED_PIN, HIGH);
  flipperServo.write(120);
  delay(300);
  flipperServo.write(0);
  delay(400);
  digitalWrite(LED_PIN, LOW);
}

void setup() {
  Serial.begin(115200);

  pinMode(LED_PIN, OUTPUT);

  esc.attach(ESC_PIN, ESC_MIN_US, ESC_MAX_US);
  flipperServo.attach(SERVO_PIN, 500, 2400);

  flipperServo.write(0);
  stopMotor();

  delay(3000);
}

void loop() {
  if (!Serial.available()) return;

  switch (Serial.read()) {
    case 'w': setMotorSpeed(50); break;
    case 'x': setMotorSpeed(100); break;
    case 's': stopMotor(); break;
    case 'q':
      if (BIDIRECTIONAL_ESC) setMotorSpeed(-40);
      break;
    case 'f': fireFlipper(); break;
    case '+': setMotorSpeed(currentSpeed + 10); break;
    case '-': setMotorSpeed(currentSpeed - 10); break;
    default: break;
  }
}
