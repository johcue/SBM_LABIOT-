#include "esp_camera.h"
#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

//
// WARNING!!! PSRAM IC required for UXGA resolution and high JPEG quality
//            Ensure ESP32 Wrover Module or other board with PSRAM is selected
//            Partial images will be transmitted if image exceeds buffer size
//
//            You must select partition scheme from the board menu that has at least 3MB APP space.
//            Face Recognition is DISABLED for ESP32 and ESP32-S2, because it takes up from 15
//            seconds to process single frame. Face Detection is ENABLED if PSRAM is enabled as well

// ===================
// Select camera model
// ===================
//#define CAMERA_MODEL_WROVER_KIT // Has PSRAM
//define CAMERA_MODEL_ESP_EYE  // Has PSRAM
//#define CAMERA_MODEL_ESP32S3_EYE // Has PSRAM
//#define CAMERA_MODEL_M5STACK_PSRAM // Has PSRAM
//#define CAMERA_MODEL_M5STACK_V2_PSRAM // M5Camera version B Has PSRAM
//#define CAMERA_MODEL_M5STACK_WIDE // Has PSRAM
//#define CAMERA_MODEL_M5STACK_ESP32CAM // No PSRAM
//#define CAMERA_MODEL_M5STACK_UNITCAM // No PSRAM
//#define CAMERA_MODEL_M5STACK_CAMS3_UNIT  // Has PSRAM
#define CAMERA_MODEL_AI_THINKER // Has PSRAM
//#define CAMERA_MODEL_TTGO_T_JOURNAL // No PSRAM
//#define CAMERA_MODEL_XIAO_ESP32S3 // Has PSRAM
// ** Espressif Internal Boards **
//#define CAMERA_MODEL_ESP32_CAM_BOARD
//#define CAMERA_MODEL_ESP32S2_CAM_BOARD
//#define CAMERA_MODEL_ESP32S3_CAM_LCD
//#define CAMERA_MODEL_DFRobot_FireBeetle2_ESP32S3 // Has PSRAM
//#define CAMERA_MODEL_DFRobot_Romeo_ESP32S3 // Has PSRAM
#include "camera_pins.h"

// BEGIN define bombs

LiquidCrystal_I2C lcd(0x27, 16, 2);


WiFiClient espClient;
PubSubClient client(espClient);
#define BOMB_CAFE 13  //cam  placa 4 
#define BOMB_LECHE 14 //cam placa 6

#define I2C_SDA 12   //lcd  placa 3
#define I2C_SCL 15   //lcd  placa 5

// END DEF

// Configuración MQTT
const char* mqtt_server = "broker.hivemq.com";
const char* topic = "bebida/gesto";

bool wait_select = false;


// ===========================
// Enter your WiFi credentials
// ===========================
//const char* password = "?wV78840"; //"s1jzsjkw5b";
//const char* ssid = "LAPTOP-U0VT893B 6544"; //"WiFi-LabIoT"; //acces point

//const char* ssid = "WiFi-LabIoT"; //"WiFi-LabIoT"; //acces point
//const char* password = "s1jzsjkw5b"; //"s1jzsjkw5b";

const char* ssid = "temp"; //"WiFi-LabIoT"; //acces point
const char* password = "@81e:12T8!!"; //"s1jzsjkw5b";

//char dirip; 

void startCameraServer();
void setupLedFlash(int pin);



void setup() {
  Serial.begin(9600);
  // Inicializar bus I2C con pines personalizados
  Wire.begin(I2C_SDA, I2C_SCL);
  Serial.setDebugOutput(true);
  Serial.println();
  // Inicializar el LCD
  lcd.init();        // Inicializar el módulo LCD
  lcd.backlight();   // Encender la luz de fondo del LCD
 /*
  lcd.setCursor(0, 0);  // Establecer el cursor en la fila 0, columna 0
  lcd.print("Hola, Mundo!");  // Imprimir un mensaje
  lcd.setCursor(0, 1);  // Mover el cursor a la fila 1, columna 0
  lcd.print("ESP32 funcionando");
  lcd.setCursor(0, 3);  // Mover el cursor a la fila 1, columna 0
  lcd.print(WiFi.localIP());
  delay(4000);
  lcd.clear();
*/
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG;  // for streaming
  //config.pixel_format = PIXFORMAT_RGB565; // for face detection/recognition
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  // if PSRAM IC present, init with UXGA resolution and higher JPEG quality
  //                      for larger pre-allocated frame buffer.
  if (config.pixel_format == PIXFORMAT_JPEG) {
    if (psramFound()) {
      config.jpeg_quality = 8; //old 10
      config.fb_count = 1; //2 old
      config.grab_mode = CAMERA_GRAB_LATEST;
      config.frame_size = FRAMESIZE_240X240; //old sin esta linea

    } else {
      // Limit the frame size when PSRAM is not available
      config.frame_size = FRAMESIZE_SVGA;
      config.fb_location = CAMERA_FB_IN_DRAM;
    }
  } else {
    // Best option for face detection/recognition
    config.frame_size = FRAMESIZE_240X240;
#if CONFIG_IDF_TARGET_ESP32S3
    config.fb_count = 2;
#endif
  }



//pinmode bombas
  pinMode(BOMB_CAFE, OUTPUT);
  pinMode(BOMB_LECHE, OUTPUT);

  digitalWrite(BOMB_CAFE, HIGH);
  digitalWrite(BOMB_LECHE, HIGH);

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t *s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1);        // flip it back
    s->set_brightness(s, 1);   // up the brightness just a bit
    s->set_saturation(s, -2);  // lower the saturation
  }
  // drop down frame size for higher initial frame rate
  if (config.pixel_format == PIXFORMAT_JPEG) {
    s->set_framesize(s, FRAMESIZE_QCIF); //old FRAMESIZE_QVGA
  }

#if defined(CAMERA_MODEL_M5STACK_WIDE) || defined(CAMERA_MODEL_M5STACK_ESP32CAM)
  s->set_vflip(s, 1);
  s->set_hmirror(s, 1);
#endif

#if defined(CAMERA_MODEL_ESP32S3_EYE)
  s->set_vflip(s, 1);
#endif

// Setup LED FLash if LED pin is defined in camera_pins.h
#if defined(LED_GPIO_NUM)
  setupLedFlash(LED_GPIO_NUM);
#endif

  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  startCameraServer();

  lcd.clear();  // Limpiar el LCD
  lcd.setCursor(0, 0);
  lcd.print("To start give me 5!");
  lcd.setCursor(0, 2);
  lcd.print("S.B.M.");

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  while (!client.connected()) {
    if (client.connect("ESP32Bebidas")) {
      client.subscribe(topic);
    } else {
      delay(500);
    }
  } 
}

void messageDisplay(String msg1, String msg2){
  lcd.clear();  // Limpiar el LCD
  lcd.setCursor(0, 0);
  lcd.print(msg1);
  lcd.setCursor(0, 2);
  lcd.print(msg2);  
}

void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  wait_select = false;

  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);


  if (message == "cafe") {
    messageDisplay("Coffe serving","......");
    digitalWrite(BOMB_CAFE, LOW); //ON
    delay(3000);
    digitalWrite(BOMB_CAFE, HIGH); //OFF
    messageDisplay("","Enjoy your beverage :)");
  } else if (message == "up5coffe") {
    messageDisplay("Coffe serving..","Ups! +5 coffes today");
    digitalWrite(BOMB_CAFE, LOW); //ON
    delay(3000);
    digitalWrite(BOMB_CAFE, HIGH); //OFF
    messageDisplay("","Enjoy your beverage :)");
  }else if (message == "leche") {
    messageDisplay("Milk serving","......");
    digitalWrite(BOMB_LECHE, LOW);   
    delay(3000);    
    digitalWrite(BOMB_LECHE, HIGH);
    messageDisplay("","Enjoy your beverage :)");
  } else if (message == "cafe_leche") {
    messageDisplay("Latte serving","......");
    digitalWrite(BOMB_CAFE, LOW);
    digitalWrite(BOMB_LECHE, LOW);
    delay(1500);
    digitalWrite(BOMB_CAFE, HIGH);
    digitalWrite(BOMB_LECHE, HIGH);
    messageDisplay("","Enjoy your beverage :)");
  } else if (message == "MENSAJE-LOGIN") {
    messageDisplay("Please gesture to me","Coffee-Milk-Latte");
    wait_select = true;
  } else if (message == "TIMEOUT") {
    messageDisplay("Timeout exceeded","Give me five again!");
  }  

  if(!wait_select) {
    delay(2000);
    messageDisplay("To start give me 5!","S.B.M.");
  }  

}

void loop() {
  client.loop();
}
