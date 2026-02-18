/*
ControllerSADA
Preliminary code for SADA module prototype
Reads in analog input from 3 sensors
Motor will move panels towards greatest value
For now, LEDs will show the direction of movement
*/

#include <Stepper.h>

const int stepsPerRevolution = 200;  // change this to fit the number of steps per revolution
Stepper myStepper(stepsPerRevolution, 2, 4, 7, 8);

int sensor1 = A1;
int sensor2 = A2;
int sensor3 = A3;
bool lightFound = false;
void setup() {
  myStepper.setSpeed(7); // set the speed at 60 rpm:
  
  Serial.begin(9600); // use the serial port
  
  pinMode(13,OUTPUT);
  digitalWrite(13,LOW);
  pinMode(0,OUTPUT);
  digitalWrite(0,LOW);
  pinMode(1,OUTPUT);
  digitalWrite(1,LOW);
}

void findLight(){
  int maxSensorValue = 0;
  int sensor2Value = 0;
  int maxStep = 0;

  maxSensorValue = analogRead(sensor2);
  
  for(int i = 0; i < stepsPerRevolution; i++){
    myStepper.step(2);
    sensor2Value = analogRead(sensor2);
    if(sensor2Value > maxSensorValue){
      maxSensorValue = sensor2Value;
      maxStep = i;
    }
    delay(20);
  }

  if(maxStep < 100)
    myStepper.step(maxStep);
  else
    myStepper.step(maxStep-stepsPerRevolution);

  lightFound = true;

}

void loop(){
  if(!lightFound){
    //findLight(); 
  }
  /*
   //Serial.print(lightFound);
   delay(200);
  */
  int sensor1Value = analogRead(sensor1);
  int sensor2Value = analogRead(sensor2);
  int sensor3Value = analogRead(sensor3);

  
  //Turn motor towards sunlight
  
  if(sensor1Value >= sensor2Value && sensor1Value >= sensor3Value){
    myStepper.step(1);
  }
  else if(sensor3Value >= sensor2Value && sensor3Value >= sensor1Value){
    myStepper.step(-1);
  }
  
  
  //Print values to console for troubleshooting
  Serial.print(sensor1Value);
  delay(20);
  Serial.print("  ");
  delay(20);
  Serial.print(sensor2Value);
  delay(20);
  Serial.print("  ");
  delay(20);
  Serial.println(sensor3Value);
  delay(20);
}
