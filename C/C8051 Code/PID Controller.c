// steering code
// 36864 = 20 ms
// 2765 = 1.5 ms
// 1659 = .9 ms
// 3871 = 2.1 ms
// *=*=*=*=*=*=*=*

//Code for a C8051 Microcontroller mounted on top of a remote control car
//Microcontroller receives sensor input from ultrasonic ranger to adjust power to wheels using PID control

#include <c8051_SDCC.h>
#include <stdio.h>
#include <stdlib.h>
#include <i2c.h>
#include <math.h>
#define NEUTRAL_HEIGHT 18      // Get from LMS, THIS MUST BE INCLUDED AFTER stdio.h
#define PCA_START 28672 // 28672 for exactly 20ms
#define PW_MAX 3459
#define PW_MIN 2002


// Function Prototypes
void Port_Init(void);   // Initialize ports for input and output
void Interrupt_Init(void);
void PCA_Init(void);
void SMB0_Init(void);
void PCA_ISR(void) __interrupt 9;
void wait(void);
void pause(void);
void Drive_motor(void);
int motorControl(void);
int ReadRanger(void);
void ADCInit(void);
unsigned char readADCInput(char n);
void cCalibration(void);
void cSteeringServo(int pwSet);
void cReadCompass(void);


// Global variables
__sbit __at 0xB6 SS;
unsigned int MOTOR_PW = 0;
int PW_NEUTRAL = 2731;
int count;
unsigned char r_count = 0;
unsigned char new_range; //flag that checks to see if new range is ready to be read
unsigned char range;
unsigned char Data[2];
signed char error;
//unsigned int Counts, nCounts/*, nOverflows*/;
int sum = 0;
unsigned char ADConversionTemp = 0;
int batteryLife;
char keypad;
//compass
unsigned char compass = 0xC0;
unsigned char cReadData[2];
int cHeading = 0;
//unsigned char cPrintCount = 0;
unsigned char cUpdate = 0;
unsigned char cUpdateCounter = 0;
int temp;
int cSteerError;
int cSteerGain = 0;
int cDesiredHeading;
//wheels
unsigned int cPulseCenter = 2775;
unsigned int cPulseMin = 2179;
unsigned int cPulseMax = 3251;
unsigned int cPulse = 36864;
unsigned int cCurPulse;
unsigned char cIsCalibrated = 0;

unsigned char LCD_Flag;

//*****************************************************************************
void main(void)
{
    Sys_Init();
	putchar(' ');
    Port_Init();
    Interrupt_Init();
    PCA_Init();
    SMB0_Init();
	ADCInit();
	cCurPulse = cPulseCenter;
	ADConversionTemp = readADCInput(7);
	printf("ADConversionTemp: %d/n/r", ADConversionTemp);
	batteryLife = ADConversionTemp * 2.4/256.0;    
    printf("\nStart\r\n");
	MOTOR_PW = PW_NEUTRAL;
	PCA0CPL2 = 0xFFFF - MOTOR_PW;
    PCA0CPH2 = (0xFFFF - MOTOR_PW) >> 8;
	PCA0CPL0 = cPulse;
    PCA0CPH0 = cPulse >> 8;
	
    count = 0;
	while(count < 40);
	printf("After motor initialization\r\n counts :%u\r\n", count);
	count = 0;
    //Counts = 0;
    while (count < 40); // Wait a long time (1s) for keypad & LCD to initialize
	cCalibration();

   lcd_clear();
    lcd_print("Please enter your slope.\n\r");

	while (keypad != 35) 
	{
		keypad = read_keypad();
		while(read_keypad() != -1);
		if ((keypad != 35) && (keypad != -1)) 
		{
				sum = (sum*10); 
				sum += (keypad - '0');
		}
       	pause();    // This pauses for 1 PCA0 counter clock cycle (20ms)        
	}

	while(keypad!=-1)
	{
		keypad = read_keypad();
	}

	printf("Slope is %u\r\n", sum);
	lcd_clear();
	lcd_print("Slope is %u.  Please enter your gain.\r\n", sum);
	
	while (keypad != 35) 
	{
		keypad = read_keypad();
		while(read_keypad() != -1);
		if ((keypad != 35) && (keypad != -1)) 
		{
				cSteerGain = (cSteerGain*10); 
				cSteerGain += (keypad - '0');
		}
       	pause();    // This pauses for 1 PCA0 counter clock cycle (20ms)        
	}

	while(keypad!=-1)
	{
		keypad = read_keypad();
	}

	printf("Gain is %u\r\n", cSteerGain);
	lcd_clear();
	lcd_print("Gain is %u.  Please enter your desired heading.\n\r", cSteerGain);

	while (keypad != 35) 
	{
		keypad = read_keypad();
		while(read_keypad() != -1);
		if ((keypad != 35) && (keypad != -1)) 
		{
				cDesiredHeading = (cDesiredHeading*10); 
				cDesiredHeading += (keypad - '0');
		}
       	pause();    // This pauses for 1 PCA0 counter clock cycle (20ms)        
	}

	printf("Desired Heading is %u\r\n", cDesiredHeading);
	lcd_clear();
	lcd_print("Desired Heading is %u.\r\n", cDesiredHeading);
	
	if(keypad == 0) printf("   **Wire Connection Error**   ");
	new_range = 1;
	
	cCalibration();
	lcd_clear();
    while (1 && cIsCalibrated) 
	{
		
		ADConversionTemp = readADCInput(7);
		batteryLife = 100*ADConversionTemp/256.0;    
		printf("Battery: %u mV\n\r", batteryLife);
		if(LCD_Flag>=3)
		{
			lcd_clear();
			lcd_print("Battery: %u\n\r", batteryLife);
			LCD_Flag = 0;
		}
		if(!SS) 
		{	
			if (new_range&& cUpdate) 
			{
				cReadCompass();
				cSteeringServo(cCurPulse);
				cUpdate = 0;
				range = ReadRanger();
				error = -1*(range - NEUTRAL_HEIGHT);
				//error = -1 *difference;
				new_range = 0;
				Data[0] = 0x51;  //write 0x51 to reg 0 of the ranger:
				i2c_write_data(0xE0, 0, Data, 1); // write one byte of data to reg 0 at addr
				printf("The range is %d, \n\r", range);
				printf("The integer value for the error is %d\n\r", (int) error);
				
				Drive_motor();


			}
		}
		else 
		{

			printf("The slide Switch is off!\n\r");
			error = 0;
			Drive_motor();
		}

		
    }
}

void Port_Init() 
{	//0x05
    XBR0 = 0x27;
	P3MDOUT &= ~0x40;
	P3 |= 0x40;
	P1MDIN &= ~0x80;
	P1MDOUT &= ~0x80;
	P1MDOUT |= 0x05;  //set output pin for CEX2 in push-pull mode
	P1 |= 0x80;
	P0MDOUT = 0xC0;    // NOTE: Only UART0 & SMB enabled; SMB on P0.2 & P0.3
}

void Interrupt_Init() {
    IE |= 0x02;
    EIE1 |= 0x08;
    EA = 1;
}

void PCA_Init() {
    PCA0MD = 0x81;      // SYSCLK/12, enable CF interrupts, suspend when idle
	PCA0CPM0 = 0xC2;
    PCA0CPM2 = 0xC2;    // 16 bit, enable compare, enable PWM; NOT USED HERE
    PCA0CN |= 0x40;     // enable PCA
}

void PCA_ISR() __interrupt 9 {
	count++;
	if (CF) {
		CF = 0;                     // clear the interrupt flag
		//nOverflows++;               // continuous overflow counter
        //nCounts++;
        PCA0L = PCA_START & 0xFF;   // low byte of start count
        PCA0H = PCA_START >> 8;     // high byte of start count
		cUpdateCounter++;
		//cPrintCount++;
		/*
		if(cUpdateCounter > 20) {
			cUpdate = 1;
			cUpdateCounter = 0;}
		*/
        /*if(nCounts > 50) {
            nCounts = 0;
            Counts++;               // seconds counter
        }*/
		r_count++;
		if(r_count >= 4) {
			new_range = 1;
			cUpdate = 1; // 4 overflows is about 80 ms
			r_count = 0;
			LCD_Flag++;
		}
     }
     else PCA0CN &= 0xC0;           // clear all other 9-type interrupts
}

void pause() {
    count = 0;
	while(count < 1);
	/*nCounts = 0;
    while (nCounts < 1);// 1 count -> (65536-PCA_START) x 12/22118400 = 20ms*/
}                      // 6 counts avoids most of the repeated hits

void wait() {
	while(count < 50);
    /*nCounts = 0;
    while (nCounts < 50);    // 50 counts -> 50 x 20ms = 1000ms*/
}

void Drive_motor() {
	MOTOR_PW = motorControl();    //increase PW
	printf("MOTOR_PW: %u\n\r", MOTOR_PW);
	PCA0CPL2 = 0xFFFF - MOTOR_PW;
	PCA0CPH2 = (0xFFFF - MOTOR_PW) >> 8;
}

int ReadRanger() {
	int hiddenRange;
	hiddenRange = 0;
	// the address of the ranger is 0xE0
	i2c_read_data(0xE0, 2, Data, 2); // read two bytes, starting at reg 2
	hiddenRange = (((unsigned int)Data[0] << 8) | Data[1]);
	return hiddenRange;
}

void SMB0_Init() {
	SMB0CR=0x93;
	ENSMB=1;
}

int motorControl() {
	if (error == 0) return 2731;
	else { 
		temp =(sum*error + 2731);
		if (temp < PW_MAX && temp > PW_MIN) return (int) temp;
		else if (temp > PW_MAX) return 3459;
		else if (temp < PW_MIN) return 2002;
		else return 2731;
	}
}

void ADCInit(void) {
	REF0CN = 0x03;
	ADC1CN = 0x80;
	ADC1CF |= 0x01;
}

unsigned char readADCInput(char n) {
	AMX1SL = n;
	ADC1CN &= ~0x20;
	ADC1CN |= 0x10;
	while((ADC1CN & 0x20) == 0x00);
	return ADC1;
}

void cCalibration() 
{
	// function to calibrate the steering. 3 steps: center, right, left.
	// at the end, sets cIsCalibrated to 1.
	char temp2 = 0;
	unsigned char step = 0;
	printf("Embedded Control Steering Calibration\n");
	while(!cIsCalibrated) {
		while(step == 0) {
			if(!temp2) {
				printf("\r\nCalibration step 1 of 3: center steering.");
				printf("\r\nPress 'l' to turn left, 'r' to turn right, 'o' to save and continue.");
				temp2 = 1;
			}
			temp = getchar();
			cSteeringServo(cPulseCenter);
			if(temp == 'r') cPulseCenter += 10;
			else if(temp == 'l') cPulseCenter -= 10;
			else if(temp == 'o') {
				printf("\r\nStep 1 complete.\r\ncPulseCenter = %u.", cPulseCenter);
				temp2 = 0;
				++step;
			}
			temp = 0;
		}
		while(step == 1) {
			if(!temp2) {
				printf("\r\nCalibration step 2 of 3: maximum right.");
				printf("\r\nPress 'l' to turn left, 'r' to turn right, 'o' to save and continue.");
				temp2 = 1;
			}
			temp = getchar();
			cSteeringServo(cPulseMax);
			if(temp == 'r') cPulseMax += 10;
			else if(temp == 'l') cPulseMax -= 10;
			else if(temp == 'o') {
				printf("\r\nStep 2 complete.\r\ncPulseMax = %u.", cPulseMax);
				temp2 = 0;
				++step;
			}
			temp = 0;
		}
		while(step == 2) {
			if(!temp2) {
				printf("\r\nCalibration step 3 of 3: maximum left.");
				printf("\r\nPress 'l' to turn left, 'r' to turn right, 'o' to save and continue.");
				temp2 = 1;
			}
			temp = getchar();
			cSteeringServo(cPulseMin);
			if(temp == 'r') cPulseMin += 10;
			else if(temp == 'l') cPulseMin -= 10;
			else if(temp == 'o') {
				printf("\r\nStep 3 complete.\r\ncPulseMin = %u.", cPulseMin);
				temp2 = 0;
				++step;
			}
			temp = 0;
		}
		if(step == 3) cIsCalibrated = 1;
	}
}
void cSteeringServo(int pwSet) 
{
	int tempFix;
	if(cIsCalibrated) {
		if(SS){ pwSet = cPulseCenter;
		printf("hello");}
		else {
			cSteerError = cDesiredHeading - cHeading;
			if(cSteerError >= 1800) cSteerError -= 3600;
			else if(cSteerError < -1800) cSteerError += 3600;
			tempFix = cSteerError * cSteerGain;
			pwSet = cPulseCenter + tempFix;
			printf("%u\r\npwSet equals", pwSet);

			
			if(pwSet > cPulseMax) pwSet = cPulseMax;
			else if(pwSet < cPulseMin) pwSet = cPulseMin;
		}
	}

	cCurPulse = pwSet;
    PCA0CPL0 = 0xFFFF - pwSet;
    PCA0CPH0 = (0xFFFF - pwSet) >> 8;
} 





void cReadCompass() 
{
	i2c_read_data(compass, 2, cReadData, 2);
	cHeading = ((unsigned int) cReadData[0]<<8) | cReadData[1];
	printf("%u\r\nheading equals",cHeading);
}