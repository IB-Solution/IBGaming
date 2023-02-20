#include "Mouse.h"

String inputData;                               //Données STR d'entrée
int inputValueX = 0;                            //Valeur d'entré
int inputValueY = 0;                            //Valeur d'entré

String getValue(String data, char separator, int index){
  int found = 0;
  int strIndex[] = { 0, -1 };
  int maxIndex = data.length() - 1;

  for (int i = 0; i <= maxIndex && found <= index; i++) {
    if (data.charAt(i) == separator || i == maxIndex) {
      found++;
      strIndex[0] = strIndex[1] + 1;
      strIndex[1] = (i == maxIndex) ? i+1 : i;
    }
  }
  return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(1);
  Mouse.begin();
}

void loop() {
  inputData = Serial.readString();
  if(inputData != ""){
    inputValueX = getValue(inputData,';',0).toInt();
    inputValueY = getValue(inputData,';',1).toInt();
    //Serial.print("move to :");Serial.println(inputData);
    Mouse.move(inputValueX, inputValueY, 0);
  }
  delay(1);
}
