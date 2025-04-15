#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>
#include <RTClib.h>
#include <SdFat.h>

#define SH110X_NO_SPLASH
// Définition des broches et constantes
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define BUTTON_STOP 6
#define BUTTON_SCREEN 5
#define BUTTON_SCREEN_OFF 10
#define LED_PIN 13
#define CHIP_SELECT 4
#define MEASURE_INTERVAL 10000
#define SCREEN_TIMEOUT 20000
#define BATTERY_PIN A7
#define LOW_BATTERY_VOLTAGE 3.2

// Objets capteurs et périphériques
Adafruit_BME280 bme;
Adafruit_SH1107 display = Adafruit_SH1107(64, 128, &Wire);
RTC_DS3231 rtc;
SdFat sd;
SdFile dataFile;

// Variables globales
char filename[13];
unsigned long lastScreenOnTime;
unsigned long lastLogTime = 0;
bool screenActive = true;
bool fileOpen = false;
bool lowBatteryAlert = false;
int lastRecordedDay = -1;

void setup() {
    pinMode(BUTTON_STOP, INPUT_PULLUP);
    pinMode(BUTTON_SCREEN, INPUT_PULLUP);
    pinMode(BUTTON_SCREEN_OFF, INPUT_PULLUP);
    pinMode(LED_PIN, OUTPUT);
    Serial.begin(115200);

    if (!bme.begin(0x76)) {
        Serial.println("Erreur capteur BME280");
        while (1);
    }

    if (!rtc.begin()) {
        Serial.println("Erreur RTC DS3231");
        while (1);
    }

    if (!sd.begin(CHIP_SELECT, SD_SCK_MHZ(12))) {
        Serial.println("Erreur carte SD");
        while (1);
    }

    if (!display.begin(0x3C, true)) {
        Serial.println("Erreur écran OLED SH110X");
        while (1);
    }
    delay(100);
    display.clearDisplay();
    display.display();
    display.setRotation(1);
    display.setTextSize(1);
    display.setTextColor(SH110X_WHITE);
    createNewLogFile();
    lastScreenOnTime = 0;
}

void loop() {
    DateTime now = rtc.now();
    if (now.day() != lastRecordedDay) {
        closeLogFile();
        createNewLogFile();
    }

    if (isIntervalElapsed(lastLogTime, MEASURE_INTERVAL)) {
        lastLogTime = rtc.now().unixtime();
        logData();
    }

    if ((!lowBatteryAlert && isIntervalElapsed(lastScreenOnTime, SCREEN_TIMEOUT) && screenActive) || (digitalRead(BUTTON_SCREEN_OFF) == LOW)) {
        turnOffDisplay();

    }

    if (digitalRead(BUTTON_SCREEN) == LOW && !screenActive) {
        turnOnDisplay();

    }

    if (digitalRead(BUTTON_STOP) == LOW) {
        if (!screenActive)
        {
            turnOnDisplay();
        }
        closeLogFile();
        stopProgram();
    }
}

void createNewLogFile() {
    DateTime now = rtc.now();
    snprintf(filename, sizeof(filename), "%02d%02d%02d.dat", now.day(), now.month(), now.year() % 100);

    if (!dataFile.open(filename, O_CREAT | O_WRITE)) {
        Serial.println("Erreur création fichier");
        return;
    }
    fileOpen = true;
    lastRecordedDay = now.day();
    Serial.print("Fichier ouvert: ");
    Serial.println(filename);
}

void logData() {
    if (!fileOpen) return;

    DateTime now = rtc.now();
    float temp = bme.readTemperature();
    float pressure = bme.readPressure() / 100.0F;
    float humidity = bme.readHumidity();
    float batteryVoltage = readBatteryVoltage();

    unsigned long timestamp = now.unixtime();
    dataFile.printf("%lu,%.2f,%.2f,%.2f,%.2f\n", timestamp, temp, pressure, humidity, batteryVoltage);
    dataFile.flush();

    if (batteryVoltage < LOW_BATTERY_VOLTAGE) {
        lowBatteryAlert = true;
        displayLowBatteryAlert();
    } else if (screenActive) {
        displayData(now, temp, pressure, humidity, batteryVoltage);
    }
}

void displayData(DateTime now, float temp, float pressure, float humidity, float batteryVoltage) {
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SH110X_WHITE);
    display.setCursor(0, 0);
    display.printf("%02d/%02d/%02d %02d:%02d:%02d\n", now.day(), now.month(), now.year() % 100, now.hour(), now.minute(), now.second());
    display.printf("Temp: %.2f C\n", temp);
    display.printf("Press: %.2f hPa\n", pressure);
    display.printf("Hum: %.2f %%\n", humidity);
    display.printf("Batt: %.2f V\n", batteryVoltage);
    display.display();
}

void displayLowBatteryAlert() {
    turnOnDisplay();
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SH110X_WHITE);
    display.setCursor(0, 20);
    display.println("BATTERY LOW!");
    display.display();
}

float readBatteryVoltage() {
    return (analogRead(BATTERY_PIN) * 3.3) / 1023.0 * 2;

}

void turnOffDisplay() {
    const uint8_t init[] = {SH110X_DISPLAYOFF};
    display.oled_commandList(init, sizeof(init));
    screenActive = false;
}

void turnOnDisplay() {
    const uint8_t init[] = {SH110X_DISPLAYALLON_RESUME, SH110X_NORMALDISPLAY};
    display.oled_commandList(init, sizeof(init));
    delay(100);
    display.oled_command(SH110X_DISPLAYON);
    screenActive = true;
    lastScreenOnTime = millis();
}

void closeLogFile() {
    if (fileOpen) {
        dataFile.close();
        Serial.println("Fichier fermé.");
        fileOpen = false;
    }
}

void stopProgram() {
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SH110X_WHITE);
    display.setCursor(0, 20);
    display.println("Program stopped!");
    display.display();
    while (true) {
        digitalWrite(LED_PIN, HIGH);
        delay(500);
        digitalWrite(LED_PIN, LOW);
        delay(500);
    }
}

bool isIntervalElapsed(unsigned long lastTimestamp, unsigned long intervalMs) {
    unsigned long currentTime = rtc.now().unixtime();
    return (currentTime - lastTimestamp >= intervalMs / 1000);
}
