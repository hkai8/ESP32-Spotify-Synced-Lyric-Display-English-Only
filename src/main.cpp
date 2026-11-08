#include <Arduino.h>
#include <Adafruit_GFX.h> // for drawing, text, shapes, colors
#include <Adafruit_ST7789.h> // the driver for this specific screen chip

Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

const int TITLE_Y = 0, TITLE_H = 22;
const int LYRIC_Y = 26, LYRIC_H = 82;
const int NEXT_Y = 112, NEXT_H = 23;

String line = "";

void showText(const String &text, int top, int height, int size, uint16_t color) {
  tft.fillRect(0, top, 240, height, ST77XX_BLACK);
  tft.setTextSize(size);
  tft.setTextColor(color);

  const int margin = 4;
  const int charW = 6 * size; // each is 6 px wide at size 1
  const int rowH = 8 * size + 2; // 8 px tall at size 1 with 2 px of space
  const int maxChars = (240 - 2 * margin) / charW; // subtract margins, a margin on each size

  int n = text.length();
  int start = 0;
  int y = top + 2;

  while (start < n && y + 8 * size <= top + height) { // while has characters to print and wont go off board
    int end;
    if (n - start <= maxChars) { // reached last line to print
      end = n;
    } else {
      int space = text.lastIndexOf(' ', start + maxChars);
      end = (space > start) ? space : start + maxChars; //if no space then returns -1 so checks if there is a space, if not print the whole 20 characters, cuts it
    }

    tft.setCursor(margin, y);
    tft.print(text.substring(start, end));

    start = end;
    while (start < n && text[start] == ' ') start++; // skip spaces before the next row
    y += rowH;
  }
}

// handle messages with protocol on how to show
void handleMessage(const String &msg) {
  if (msg.length() == 0 || (msg.length() >= 2 && msg[1] != ';')) {
    Serial.println("err");
    return;
  }
  char type = msg[0];
  String body = (msg.length() >= 2) ? msg.substring(2) : "";

  if (type == 'T') {
    showText(body, TITLE_Y, TITLE_H, 1, ST77XX_GREEN);
    // title in green, size 1
  } else if (type == 'L') {
    showText(body, LYRIC_Y, LYRIC_H, 2, ST77XX_WHITE);
    // show lyric in white
  } else if (type == 'C') {
    tft.fillScreen(ST77XX_BLACK);
  } else if (type == 'N') {
    showText(body, NEXT_Y, NEXT_H, 1, tft.color565(130, 130, 130));
  } else {
    Serial.println("err");
    return;
  }
  Serial.println("ok");
  delay(2);
}

void setup() {
  Serial.begin(115200);

  pinMode(TFT_I2C_POWER, OUTPUT);
  digitalWrite(TFT_I2C_POWER, HIGH);
  pinMode(TFT_BACKLITE, OUTPUT);
  digitalWrite(TFT_BACKLITE, HIGH);

  delay(10);

  tft.init(135, 240);
  tft.setRotation(3);
  tft.fillScreen(ST77XX_BLACK);

  showText("Waiting for computer...", TITLE_Y, TITLE_H, 1, ST77XX_GREEN);
}

void loop() {
  while(Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      handleMessage(line);
      line = "";
    } else if (c == 8 || c == 127) {
      if (line.length() > 0)
        line = line.substring(0, line.length() - 1);
    } else if (c != '\r') {
      line += c;
    }
  }
}

// String line = "";

// // shows whatever is stored in text on screen at 10, 10
// void show(const String &text) {
//   tft.fillScreen(ST77XX_BLACK);
//   const int maxChars = 19;
//   int n = text.length();
//   int start = 0;
//   int y = 10;

//   while (start < n && y + 16 <= 135) { // while has characters to print and wont go off board
//     int end;
//     if (n - start <= maxChars) { // reached last line to print
//       end = n;
//     } else {
//       int space = text.lastIndexOf(' ', start + maxChars);
//       end = (space > start) ? space : start + maxChars; //if no space then returns -1 so checks if there is a space, if not print the whole 20 characters, cuts it
//     }

//     tft.setCursor(10, y);
//     tft.print(text.substring(start, end));

//     start = end;
//     while (start < n && text[start] == ' ') start++; // skip spaces before the next row
//     y += 18;
//   }
// }

// void setup() {
//   Serial.begin(115200); // start USB serial port

//   pinMode(TFT_I2C_POWER, OUTPUT);
//   digitalWrite(TFT_I2C_POWER, HIGH);
//   delay(10);
//   pinMode(TFT_BACKLITE, OUTPUT);
//   digitalWrite(TFT_BACKLITE, HIGH);

//   tft.init(135, 240);
//   tft.setRotation(3);
//   tft.setTextSize(2); // each character approx 12 px wide 
//   tft.setTextColor(ST77XX_WHITE);

//   show("Type something");
// }

// void loop() {
//   while (Serial.available()) {
//     // any bytes waiting?
//     char c = Serial.read();

//     if (c == '\n') {
//       if (line.equals("clear")) tft.fillScreen(ST77XX_BLACK);
//       else show(line); // reached end of line so show the current most recently typed line
//       Serial.println("ok");
//       line = "";
//     } else if (c == 8 || c == 127) {
//       if (line.length() > 0) {
//         line.remove(line.length() -1); // remove the last character because backspaced
//       }
//     }
//     else if (c != '\r') { // \r is the carriage return, goes back to start of the line
//       // platformIO sends both \r\n at end of each line when enter is pressed
//       line += c;
//     }
//   }
// }

// int counter = 0;
// void setup() {
//   //set up screen 
//   pinMode(TFT_I2C_POWER, OUTPUT);
//   digitalWrite(TFT_I2C_POWER, HIGH); // turn on screen
//   delay(10); //give time to power on
//   pinMode(TFT_BACKLITE, OUTPUT);
//   digitalWrite(TFT_BACKLITE, HIGH); // turn on backlite

//   // set size of screen
//   tft.init(135, 240);
//   tft.setRotation(3); // landscape
//   // top left is (0,0) y grows downwards

//   tft.fillScreen(ST77XX_BLACK);
//   // black screen
//   tft.setTextSize(3);
//   tft.setTextColor(ST77XX_GREEN);
//   tft.setCursor(10,20);
//   tft.print("Hello!"); // prints wherever cursor is

//   tft.setCursor(10, 55);
//   tft.print("Kailin");

//   tft.fillRect(200, 20, 30, 30, ST77XX_WHITE);
//   tft.setTextColor(ST77XX_WHITE);
// }

// void loop() {
//   counter++;
//   tft.fillRect(10, 95, 220, 24, ST77XX_BLACK);
//   tft.setCursor(10, 95);
//   tft.print(counter);
//   delay(1000);
// }
