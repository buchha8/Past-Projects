//Code for Dynamic Pot Stirrer
//Written by Alexander Buchholz
//Last updated 11/30/14
//This code allows the user to control the pot stirrer's timer, as well as
//reading temperature, adjusting motor speed, and displaying information

#include <SoftwareSerial.h>
#include <i2cmaster.h>

//pin definitions
const int MOTOR_ON = 3;
const int BUZZER = 6;
const int SPEED_READ = 2;
const int BUTTON_UP = 12;
const int BUTTON_DOWN = 8;
const int TIMER_BUTTON = 13;

// Attach the LCD display's RX line to digital pin 2
SoftwareSerial LCD(9,7); // pin 7 = TX, pin 9 = RX (unused)

int motor_speed = 0;
const unsigned int danger_thresh = 150;
//default temperature if thermometer does not read
int temperature = 50;
int seconds = 60;

//various flags
boolean timer_activate = false;
boolean LCD_blink = true;
boolean timer_enable = true;
boolean buzzer_enable = false;
boolean toggle1 = 0;

void setup()
{
  
   pinMode(MOTOR_ON,OUTPUT);
   analogWrite(MOTOR_ON,0);
   pinMode(BUZZER, OUTPUT);
   
   pinMode(BUTTON_UP,INPUT);
   pinMode(BUTTON_DOWN,INPUT);
   pinMode(TIMER_BUTTON,INPUT);
   analogWrite(BUZZER, 10);
   cli();//stop interrupts
   
   //set timer1 interrupt at 1Hz
   TCCR1A = 0;// set entire TCCR1A register to 0
   TCCR1B = 0;// same for TCCR1B
   TCNT1  = 0;//initialize counter value to 0
   // set compare match register for 1hz increments
   OCR1A = 15624;// = (16*10^6) / (1*1024) - 1 (must be <65536)
   // turn on CTC mode
   TCCR1B |= (1 << WGM12);
   // Set CS12 and CS10 bits for 1024 prescaler
   TCCR1B |= (1 << CS12) | (1 << CS10);  
   // enable timer compare interrupt
   TIMSK1 |= (1 << OCIE1A);
   
   sei();//allow interrupts
   
   LCD.begin(9600); // set up serial port for 9600 baud
   
   i2c_init(); //Initialise the i2c bus
   PORTC = (1 << PORTC4) | (1 << PORTC5);//enable pullups
   
}

//function for reading infrared thermometer
int tempRead()
{
    int dev = 0x5A<<1;
    int data_low = 0;
    int data_high = 0;
    int pec = 0;
    
    i2c_start_wait(dev+I2C_WRITE);
    i2c_write(0x07);
    
    // read
    i2c_rep_start(dev+I2C_READ);
    data_low = i2c_readAck(); //Read 1 byte and then send ack
    data_high = i2c_readAck(); //Read 1 byte and then send ack
    pec = i2c_readNak();
    i2c_stop();
    
    //This converts high and low bytes together and processes temperature, MSB is a error bit and is ignored for temps
    double tempFactor = 0.02; // 0.02 degrees per LSB (measurement resolution of the MLX90614)
    double tempData = 0x0000; // zero out the data
    int frac; // data past the decimal point
    
    // This masks off the error bit of the high byte, then moves it left 8 bits and adds the low byte.
    tempData = (double)(((data_high & 0x007F) << 8) + data_low);
    tempData = (tempData * tempFactor)-0.01;
    double celsius = tempData - 273.15;
    int fahrenheit = (int)(((celsius)*1.8) + 32);
    return fahrenheit;
}

void clearScreen()
{
  //clears the screen
  LCD.write(0xFE);
  LCD.write(0x01); 
}

void selectLineOne()
{ 
  //puts the cursor at line 0 char 0.
  LCD.write(0xFE); //command flag
  LCD.write(128); //position
}
//-------------------------------------------------------------------------------------------
void selectLineTwo()
{ 
  //puts the cursor at line 0 char 0.
  LCD.write(0xFE); //command flag
  LCD.write(192); //position
}

 
//main function to update LCD with time and temperature
void LCDdisplay(int display_seconds, int display_temperature) {
  int minutes;
  minutes = display_seconds / 60;
  display_seconds = display_seconds - minutes * 60;
  
  clearScreen();
  selectLineOne();
  LCD.print("Time: ");
  
  //blink time when timer is not running
  if(!timer_activate)
  {
    LCD_blink = !LCD_blink;
  }
  
  if(!LCD_blink)
  {
    LCD.print(minutes);
    printDigits(display_seconds);
  }
   
  selectLineTwo();
  LCD.print("Temperature:");
  LCD.print(display_temperature);
  LCD.print("F");
}
 

//function to format time
void printDigits(int digits) 
{
  LCD.print(":");
  if(digits < 10)
    LCD.print('0');
  LCD.print(digits);
}

//updates LCD on timer1 overflow
ISR(TIMER1_COMPA_vect)
{//timer1 interrupt 1Hz
  temperature = tempRead();
  if(seconds > 0 && timer_activate)
  {  
    LCD_blink = false;
    seconds--;
    LCDdisplay(seconds, temperature);
  }
  else
  {
    timer_activate = false;
    if(buzzer_enable && seconds == 0)
      analogWrite(BUZZER, 10);
    else if(temperature < danger_thresh)
    {    
      analogWrite(BUZZER, 0);
    }
    LCDdisplay(seconds, temperature);
    buzzer_enable = !buzzer_enable;
  } 
}

//main loop constantly checking for user input
void loop()
{
  motor_speed = (analogRead(SPEED_READ)/20);

  //adjust motor speed based off of potentiometer reading
  if(timer_activate && seconds > 0 && motor_speed > 10)
  {
    analogWrite(MOTOR_ON, 100+motor_speed);
  }
  else
  {
    analogWrite(MOTOR_ON, 0);
  }
  
  //ring buzzer if dangerous temperature
  if(temperature >= danger_thresh)
  {
    analogWrite(BUZZER, 10);
    timer_activate = false;
  }
 
  
  if(digitalRead(BUTTON_UP) && !timer_activate)
  {
    seconds += 1;
    LCDdisplay(seconds, temperature);
    delay(100);
  }
  
  if(digitalRead(BUTTON_DOWN) && !timer_activate)
  {
    if(seconds-1>=0)
      seconds -= 1;
    else
      seconds = 0;
    LCDdisplay(seconds, temperature);
    delay(100);
  }
  
  
  if(digitalRead(TIMER_BUTTON))
  {
      timer_activate = !timer_activate;
      //set interrupt value close to max, so that the number counts down immediately upon cancelization
      TCNT1  = 15623;
      delay(1000);
  }
}

