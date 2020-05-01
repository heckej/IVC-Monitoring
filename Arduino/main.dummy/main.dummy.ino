// Calculate based on max input size expected for one command
#define INPUT_SIZE 30
/* Code for dummy cage */
const char* cageID = "A2"; // Kooi nr (letter A-H + getal 1-10)
const int limietWater = 50;
const int foodLed = 6; // LED food shortage
const int waterLed = 4; // LED water shortage
void setup() {
 // Log naar de seriële monitor
 // Later: laat LED branden, stuur door naar webserver
 Serial.begin(9600);
 Serial.print(cageID);
 Serial.println(" ready");
 pinMode(foodLed, OUTPUT);
 pinMode(waterLed, OUTPUT);
 randomSeed(analogRead(0));
}

void loop() {
  String cmdVal[2];
  if(Serial.available() > 0) {
    // Get command (and value) from Raspberry Pi
    getCommand(cmdVal);
    String cmd = cmdVal[0];
    String val = cmdVal[1];
    /*Serial.println(cmd); // for debugging only
    Serial.println(val);*/ 
    if(cmd.equals("blink")) {
        // knipper
        
    } else if(cmd.equals("measure")) {
        printMeasurements();
    } else if(cmd.equals("ledOn")) {
        // turn on led
        if(val == "food") {
          digitalWrite(foodLed, HIGH);
          Serial.println("food led on");
        } else if(val == "water") {
          digitalWrite(waterLed, HIGH);
          Serial.println("food led on");
        }
    } else if(cmd.equals("ledOff")) {
        // turn off led
        if(val == "food") {
          digitalWrite(foodLed, LOW);
          Serial.println("food led off");
        } else if(val == "water") {
          digitalWrite(waterLed, LOW);
          Serial.println("water led off");
        }
    } else {
      Serial.print(cageID);
      Serial.println("unknownCmd");
    }
  }
}
void printMeasurements() {  
  Serial.print(cageID);
  Serial.print(":");
   
  // Meet etensvoorraad
   int etenNodig = etenTekort();
   // Melding wanneer onvoldoende eten
   if(etenNodig == true) {
    Serial.print("1:");
    digitalWrite(foodLed, HIGH);
   } else {
    Serial.print("0:");
    digitalWrite(foodLed, LOW);
   }
   
  // Meet watervoorraad
   int meting;
   meting = meetWater();
   char water[4];
   sprintf(water, "%04d", meting);
   // Melding wanneer onvoldoende water
   if(meting < limietWater) {
    digitalWrite(waterLed, HIGH);
   } else {
    digitalWrite(waterLed, LOW);
   }
   Serial.println(water);
   delay(1000);
}

bool etenTekort() {
  return random(0,1);
}


int meetWater() {
  return random(1023);
}


void getCommand(String* commandValue) {
  String execCmd = "";
  String execVal = "";
  // Get next command from Serial (add 1 for final 0)
  char input[INPUT_SIZE + 1];
  byte size = Serial.readBytes(input, INPUT_SIZE);
  // Add the final 0 to end the C string
  input[size] = 0;
  
  // Read each command pair 
  char* command = strtok(input, ";");
  while (command != 0)
  {
      char* cmd = strtok(command, "&");
      while(cmd != 0) {
        // Split the command in two values
        char* value = strchr(cmd, ':');
        if (value != 0)
        {
            *value = 0;
            ++value;
          if(!strcmp(cmd,"cmd")) {
            //Serial.println("command");
            execCmd = value;
          } else if(!strcmp(cmd,"val")) {
            //Serial.println("value");
            execVal = value;
          }
        }
      // Find the next command in input string
      cmd = strtok(0, "&");
      }
      commandValue[0] = execCmd;
      commandValue[1] = execVal;
      /*Serial.print("Command: ");
      Serial.println(execCmd);
      Serial.print("Value: ");
      Serial.println(execVal);*/
      
      // Find the next command in input string
      command = strtok(0, ";");
  }
}
