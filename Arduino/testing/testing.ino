#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>

// 1. LCD Configuration (Address 0x27)
LiquidCrystal_I2C lcd(0x27, 16, 2);

// 2. DHT22 Sensor
#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// 3. Sensor Input Pins
const int SOIL_PIN  = A0;
const int FLOAT_PIN = 7;

// 4. Relay Output Pins (Active-LOW: LOW = ON, HIGH = OFF)
const int RELAY_PUMP = 8;
const int RELAY_FAN  = 9;
const int RELAY_MIST = 10;

// Variables to track relay states for LCD display
int pumpState = 0;
int fanState  = 0;
int mistState = 0;

unsigned long lastSend = 0;
unsigned long lastLcdUpdate = 0;

void setup() {
  Serial.begin(115200);
  dht.begin();
  pinMode(FLOAT_PIN, INPUT_PULLUP);

  // Initialize LCD
  Wire.begin();
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("LabVIEW Link...");
  delay(1500);
  lcd.clear();

  // Relays default to OFF (HIGH)
  pinMode(RELAY_PUMP, OUTPUT);
  pinMode(RELAY_FAN, OUTPUT);
  pinMode(RELAY_MIST, OUTPUT);
  digitalWrite(RELAY_PUMP, HIGH);
  digitalWrite(RELAY_FAN, HIGH);
  digitalWrite(RELAY_MIST, HIGH);
}

void loop() {
  // Read Sensors
  int soil = analogRead(SOIL_PIN);
  float hum = dht.readHumidity();
  float rawTemp = dht.readTemperature();
  int tank = (digitalRead(FLOAT_PIN) == HIGH) ? 1 : 0; // Float UP = Full (1)

  // Fahrenheit to Celsius Fix
  float tempC = rawTemp;
  if (tempC > 45.0) tempC = (tempC - 32.0) * 5.0 / 9.0;
  if (isnan(tempC)) tempC = 0.0;
  if (isnan(hum))   hum = 0.0;

  // ========================================================
  // 1. SEND CLEAN NUMERIC DATA TO LABVIEW (Every 150ms)
  // ========================================================
  if (millis() - lastSend >= 150) {
    lastSend = millis();

    // Output purely integers: e.g. "1018,65,20,1\n"
    Serial.print(soil);
    Serial.print(",");
    Serial.print((int)hum);
    Serial.print(",");
    Serial.print((int)tempC);
    Serial.print(",");
    Serial.println(tank);
  }

  // ========================================================
  // 2. RECEIVE RELAY COMMANDS FROM LABVIEW ("1,0,1\n")
  // ========================================================
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.length() >= 5) {
      pumpState = cmd.substring(0, 1).toInt();
      fanState  = cmd.substring(2, 3).toInt();
      mistState = cmd.substring(4, 5).toInt();

      // Hardware safety: If tank empty, force pump & mist OFF
      if (digitalRead(FLOAT_PIN) == LOW) { // Float DOWN = Empty (0) -> Emergency Stop
        pumpState = 0;
        mistState = 0;
      }

      // Drive Active-LOW Relays (1 = ON/LOW, 0 = OFF/HIGH)
      digitalWrite(RELAY_PUMP, (pumpState == 1) ? LOW : HIGH);
      digitalWrite(RELAY_FAN,  (fanState == 1)  ? LOW : HIGH);
      digitalWrite(RELAY_MIST, (mistState == 1) ? LOW : HIGH);
    }
  }

  // ========================================================
  // 3. UPDATE RG1602A LCD SCREEN (Every 500ms)
  // ========================================================
  if (millis() - lastLcdUpdate >= 500) {
    lastLcdUpdate = millis();

    // Line 1: Temperature, Humidity, Tank Status
    lcd.setCursor(0, 0);
    lcd.print("T:");
    lcd.print((int)tempC);
    lcd.print("C H:");
    lcd.print((int)hum);
    lcd.print("% ");
    lcd.print(tank ? "W:OK" : "W:MT");

    // Line 2: Soil Reading & Actuators (P=Pump, F=Fan, M=Mist)
    lcd.setCursor(0, 1);
    lcd.print("S:");
    lcd.print(soil);
    lcd.print(" P:");
    lcd.print(pumpState);
    lcd.print(" F:");
    lcd.print(fanState);
    lcd.print(" M:");
    lcd.print(mistState);
    lcd.print("   "); // Clears trailing chars
  }
}