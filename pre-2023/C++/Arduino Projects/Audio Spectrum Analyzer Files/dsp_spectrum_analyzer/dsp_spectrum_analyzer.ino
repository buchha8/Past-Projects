/*
dsp_spectrum_analyzer.pde
Examples on openmusiclabs were incredibly helpful when writing code and learning their library
Takes in audio input on A0, finds frequency spectrum, divides bins by octaves,
and drives LEDs on pins 6, 9, 10 and 11
*/

#define OCTAVE 1 // use the octave output function
#define FFT_N 256 // set to 256 point fft


#include <FFT.h> // include the library

//LEDs are on pins 11, 10, 9, and 6 (all PWM pins)
int led_blue = 11; // Lowest pitch
int led_green = 10;
int led_yellow = 9;
int led_red = 6; //Highest pitch

void setup() {
  Serial.begin(115200); // use the serial port
  TIMSK0 = 0; // turn off timer0 for lower jitter
  ADCSRA = 0xe5; // set the adc to free running mode
  ADMUX = 0x40; // use adc0
  DIDR0 = 0x01; // turn off the digital input for adc0
  
  //Configure all LED pins for output
  //Registers can be changed directly with bitwise operations instead of pinMode()
  //This would improve performance, but I am a bit unfamiliar with the ATMega328 architecture
  pinMode(led_blue, OUTPUT);
  pinMode(led_green, OUTPUT);
  pinMode(led_yellow, OUTPUT);
  pinMode(led_red, OUTPUT);
}

void loop() {
  while(1) { // reduces jitter
    cli();  // UDRE interrupt slows this way down on arduino1.0
    for (int i = 0 ; i < 512 ; i += 2) { // save 256 samples
      while(!(ADCSRA & 0x10)); // wait for adc to be ready
      ADCSRA = 0xf5; // restart adc
      byte m = ADCL; // fetch adc data
      byte j = ADCH;
      int k = (j << 8) | m; // form into an int
      k -= 0x0200; // form into a signed int
      k <<= 6; // form into a 16b signed int
      fft_input[i] = k; // put real data into even bins
      fft_input[i+1] = 0; // set odd bins to 0
    }
    fft_window(); // window the data for better frequency response
    fft_reorder(); // reorder the data before doing the fft
    fft_run(); // process the data in the fft
    fft_mag_octave(); // take the output of the fft and sort into octaves
    sei();
    Serial.println("start");
    for (byte i = 0 ; i < log(FFT_N)/log(2); i++) {  // desired number of bins is the base 2 log of N
      Serial.println(fft_oct_out[i]); // send out the data
    }
    
    /*Turn on LED when octave magnitude is above the threshold
    Turn the LED off if below the threshold
    Use octaves 2, 3, 4 and 5 for LEDs
    octaves 0 and 1 contain DC values, and octaves 6 and 7 are too high to use effectively
    */
    if(fft_oct_out[2] >= 110)
      analogWrite(led_blue, fft_oct_out[2]-110);
    else
      analogWrite(led_blue, 0);
    if(fft_oct_out[3] >= 85)
      analogWrite(led_green, fft_oct_out[3]-85);
    else
      analogWrite(led_green, 0);
    if(fft_oct_out[4] >= 75)
      analogWrite(led_yellow, fft_oct_out[4]-75);
    else
      analogWrite(led_yellow, 0);
    if(fft_oct_out[5] >= 65)
      analogWrite(led_red, fft_oct_out[5]-65);  
    else
      analogWrite(led_red, 0);
  }
}
