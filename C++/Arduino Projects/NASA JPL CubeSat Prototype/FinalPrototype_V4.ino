/*NASA/JPL CubeSat SADA (2)RPI Capstone Project: Spring 2016
 * 5/15/2016
 * Code used for CubeSat (2) final prototype
 * This code processes readings on the sensors, pushbutton, and encoder, and uses them to drive the SADA motor according to the prototype algorithm
 * To be used with Arduino library
 */
 
#include <Stepper.h>

//15 degrees per step
const int stepsPerRevolution = 24;

//Define pin connections
Stepper myStepper(stepsPerRevolution, 5, 6, 3, 11);
int sensor3 = A2;
int sensor2 = A0;
int sensor1 = A1;
int encoder = A5;
int pushButton = 1;

//If lightFound is false, a 360 degree check is needed
bool lightFound = false;

int encoderValue = 0;

void setup() {
  pinMode(pushButton, INPUT);
  
  myStepper.setSpeed(500);
  Serial.begin(9600);
}

//Function to locate light upon startup, and when light source is lost
//Does a 360 scan, finds the max light source, and rotates panels towards light source
void findLight(){
  int maxSensorValue = 0;
  int maxEncoder = 0;
  int maxStep = 0;
  int encoderValue = analogRead(encoder);
  int sensor2Value = analogRead(sensor2);

  //Use step values to keep track of position, read encoder to check for error
  Serial.println("360 Check");
  for(int i = 0; i < 600; i++){
    myStepper.step(10);
    encoderValue = analogRead(encoder);
    sensor2Value = analogRead(sensor2);
    
    //If new maximum light source found, log its brightness, step number, and encoder value
    if(sensor2Value > maxSensorValue){
      maxSensorValue = sensor2Value;
      maxEncoder = encoderValue;
      maxStep = i;
    }
  }
    Serial.println("Moving...");
    //Complete 360 degrees traveled, go to place with max light
    //Rotate in direction with shortest path
    if(maxStep > 300){
      for(int i = 0; i < 600-maxStep; i++){
        myStepper.step(-10);
      }
    }
    else{
      for(int i = 0; i < maxStep; i++){
        myStepper.step(10);
      }
    }
    
  Serial.print("Max encoder position: ");
  Serial.print(maxEncoder);
  Serial.print(" Current encoder position: ");
  Serial.println(analogRead(encoder));
  lightFound = true;
}


void loop() {
  int sensor1Value = analogRead(sensor1);
  int sensor2Value = analogRead(sensor2);
  int sensor3Value = analogRead(sensor3);
  int encoderValue = analogRead(encoder);
  int pushButtonValue = digitalRead(pushButton);
  //Do not do rotate panels until panels are deployed
  //Uncomment if-else block if this functionality is desired
  //if(pushButtonValue == 0)
  //{
 
    //Position lost, prepare to do 360 check again
    if(sensor1Value < 100 && sensor2Value < 100 && sensor3Value < 100){
      lightFound = false;
    }
    if(!lightFound){
      findLight();
      sensor1Value = analogRead(sensor1);
      sensor2Value = analogRead(sensor2);
      sensor3Value = analogRead(sensor3);
      encoderValue = analogRead(encoder);
      pushButtonValue = digitalRead(pushButton);
    }
  
    //if sensor 1 is brightest value, rotate on -Y axis
    if(sensor1Value >= sensor2Value && sensor1Value >= sensor3Value)
      myStepper.step(10);
    //if sensor 3 is brightest value, rotate on Y axis
    else if(sensor3Value >= sensor2Value && sensor3Value >= sensor1Value)
      myStepper.step(-10);

    //Print values for debugging
    Serial.print("Sensor1: ");
    Serial.print(sensor1Value);
    Serial.print(" Sensor2: ");
    Serial.print(sensor2Value);
    Serial.print(" Sensor3: ");
    Serial.print(sensor3Value);
    Serial.print(" Encoder: ");
    Serial.print(encoderValue);
    Serial.print(" Deployed: ");
    Serial.println(pushButtonValue);
 //}
 //else
   // Serial.println("Panels not deployed");
}
