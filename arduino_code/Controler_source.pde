
const int analogInPinRed = A0;  // Orange Wire
const int analogInPinOrange = A1;  // Red Wire

int sensorValueRed = 0;        // value read from the pot
int sensorValueOrange = 0;        // value read from the pot

int dataout;

int PrevioussensorValueRed =500;
int PrevioussensorValueOrange =500;

int fudfactor =25;

void setup() {
  // initialize serial communications at 9600 bps:
  Serial.begin(9600); 
}

void loop() {
  // read the analog in value:
 sensorValueRed = analogRead(analogInPinRed);   
 sensorValueOrange = analogRead(analogInPinOrange);



if (!(
     (sensorValueRed > (PrevioussensorValueRed - fudfactor)) &&
      (sensorValueRed < (PrevioussensorValueRed + fudfactor))&&
      (sensorValueOrange > (PrevioussensorValueOrange - fudfactor)) && 
      (sensorValueOrange < (PrevioussensorValueOrange + fudfactor)))) {
  Serial.print(sensorValueRed); 
  Serial.print(";" );   
  PrevioussensorValueRed = sensorValueRed;
  
  Serial.println(sensorValueOrange); 
  
  PrevioussensorValueOrange = sensorValueOrange;
  
  
}
delay (200);
}

