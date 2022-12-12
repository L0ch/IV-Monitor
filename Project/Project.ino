#include <Wire.h>           
#include <LiquidCrystal_I2C.h> 
#include "HX711.h" // HX711 loadCell AMP library
#include <SoftwareSerial.h>

#define calibration_factor -7070 // Scale Value
#define scale_gram 2.75 // gram Scale
#define DOUT  3 // Data Out
#define CLK  2  // Clock
#define MaxVal 350 // IV capacity

int i,j;
int cnt = 0;
double temp;
double accum = 0.0;
double arr[10] = {0.0,};
LiquidCrystal_I2C lcd(0x27,16,2);
SoftwareSerial BTSerial(4, 5);

HX711 scale(DOUT, CLK); 
void setup() {

  Serial.begin(9600);  // Serial
  BTSerial.begin(9600);

  scale.set_scale(calibration_factor);  // set scale
  scale.tare(); 

  lcd.init();                      // LCD initialization
  // Print a message to the LCD.
  lcd.backlight();        
  delay(1000);
  lcd.print("IV Capacity");


}
void loop() {
  
  
  double percent;
  double weight;

  double display_per;
  weight = scale.get_units() * scale_gram;
  percent = (weight-35.0) / MaxVal * 100.0;
  
  Serial.println(percent);
  arr[cnt] = percent;


  if(cnt == 10){

    //bubble sort
	  for(int i = 0; i < 10; i++) {       
		  for(int j= 1 ; j < 10-i; j++) { 
			  if(arr[j-1] > arr[j]) {           
              
				  temp = arr[j-1];
				  arr[j-1] = arr[j];
				  arr[j] = temp;
			  }
		  }
	  }
  

    // except Max 2 , Min 2 Value(Outlier) 
    for(i=2; i<8; i++){
      accum += arr[i];
    }
    
    display_per = accum / ((double)cnt - 4.0);

    
    lcd.clear();
    lcd.print("IV Capacity");
    lcd.setCursor(0,0);
    lcd.setCursor(0,1);
    lcd.print(display_per,1);
    lcd.print("%");
    BTSerial.println(display_per); 

    if(display_per < 20){
      lcd.setCursor(13,1);
      lcd.print("LOW");
    }

    accum = 0;
    cnt = 0;
  }
  else{
    cnt++;
  }

  delay(500);


}
