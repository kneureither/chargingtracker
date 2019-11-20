const int msg_len = 30;
const int current_pin = 0;
const float resistance = 0.1;
const float restistance_corr_factor = 0.948;
char msg[msg_len];
float resistance_corr;
bool valid_request;

int mean_delay = 50;
int stream_delay = 100;

////Functions +++++++++++++++++++++++++++++++++++++++++++++++

float ReadCurrentOnce(int pin) {
  float voltage_input = analogRead(current_pin);
  float voltage = (voltage_input / (float) 1024) * 5.0;
  float my_current = voltage / resistance_corr;
  return my_current;
}

float ReadVoltageOnce(int pin) {
  float voltage_input = analogRead(current_pin);
  return (voltage_input / (float) 1024) * 5.0;
}

float ReadCurrentMean(int pin, int mean_count) {
  float current = 0;
  for(int i = 0; i < mean_count; i++) {
    current += ReadCurrentOnce(current_pin);
    delay(mean_delay);
  }
  return current / (float) mean_count;
}

float ReadVoltageMean(int pin, int mean_count) {
  float current = 0;
  for(int i = 0; i < mean_count; i++) {
    current += ReadVoltageOnce(current_pin);
    delay(mean_delay);
  }
  return current / (float) mean_count;
}

int ReadFlagValue(String command, String flag) {
    command = command + " ";
    int flag_index = command.indexOf(flag);
    int index_left = command.indexOf(" ", flag_index + 1);
    int index_right = command.indexOf(" ", index_left + 1);
    int next_flag = command.indexOf("-", flag_index + 1);
    // no flag
    if(flag_index == -1) {
      return -1;
    }
    //missing value for flag
    else if (index_right == -1 || (next_flag != -1 && index_right >= next_flag)) {
      Serial.println("ERROR: Missing value for flag " + flag + " of command " + command.substring(0, 3));
      return -1; 
    } 
    //everything okay
    else {
      String value = command.substring(index_left + 1, index_right);
      return value.toInt();
    }   
}

String getCommandString(String tag) {
  String command;
  String message = msg;
  int com_index_left = message.indexOf(tag);
  int com_index_right = message.indexOf("?", com_index_left + 3);
  if(com_index_right == -1) {
    command = message.substring(com_index_left);
  } else {
    command = message.substring(com_index_left, com_index_right);
  }
  return command;
}



////Setup and main()++++++++++++++++++++++++++++++++++++++++++
void setup() {
  Serial.begin(9600);
  resistance_corr = resistance * restistance_corr_factor;
}

void loop() {
  String response = "";
  valid_request = false;
    
  if(Serial.available()) {
    Serial.readStringUntil('\n').toCharArray(msg, msg_len);
    String message = msg;
    
    if(strstr(msg, "A0?")) {
      valid_request = true;
      String command = getCommandString("A0?");
      int stream_count = ReadFlagValue(command, "-stream");
      int mean_count = ReadFlagValue(command, "-mean");
      valid_request = true;
      
      if (stream_count == -1 && mean_count == -1) {
        float current = ReadCurrentOnce(current_pin);
        Serial.println("A0: " + String(current) + " ");
      }
      else if(stream_count != -1 && mean_count == -1) {
        for(int i = 0; i < stream_count; i++) {
          float current = ReadCurrentOnce(current_pin);
          Serial.println("A0: " + String(current) + " delay=" + stream_delay);
          delay(stream_delay);
        }
      }
      else if(stream_count == -1 && mean_count != -1) {
        float current = ReadCurrentMean(current_pin, mean_count);
        Serial.println("A0: " + String(current) + " mean_count=" + mean_count + "delay=" + mean_delay);
      } 
      else if(stream_count != -1 && mean_count != -1) {
        for(int i = 0; i < stream_count; i++) {
          float current = ReadCurrentMean(current_pin, mean_count);
          Serial.println("A0: " + String(current) + " mean_count=" + mean_count + "delay=" + mean_delay);
        }
      }
    }
    if(strstr(msg, "V0?")) {
      valid_request = true;
      String command = getCommandString("V0?");
      int stream_count = ReadFlagValue(command, "-stream");
      int mean_count = ReadFlagValue(command, "-mean");

      if (stream_count == -1 && mean_count == -1) {
        float voltage = ReadVoltageOnce(current_pin);
        Serial.println("V0: " + String(voltage) + " ");
      }
      else if(stream_count != -1 && mean_count == -1) {
        for(int i = 0; i < stream_count; i++) {
          float voltage = ReadVoltageOnce(current_pin);
          Serial.println("V0: " + String(voltage) + " delay=" + stream_delay);
          delay(stream_delay);
        }
      }
      else if(stream_count == -1 && mean_count != -1) {
        float voltage = ReadVoltageMean(current_pin, mean_count);
        Serial.println("V0: " + String(voltage) + " mean_count=" + mean_count + "delay=" + mean_delay);
      } 
      else if(stream_count != -1 && mean_count != -1) {
        for(int i = 0; i < stream_count; i++) {
          float voltage = ReadVoltageMean(current_pin, mean_count);
          Serial.println("V0: " + String(voltage) + " mean_count=" + mean_count + "delay=" + mean_delay);
        }
      }
    } 

    //no data request but only status? request
    if(valid_request == false && strstr(msg, "Status?")) {
      valid_request = true;
      response = response +  "{ " \
                    "\"mean delay\": " + mean_delay + ", " \
                    "\"stream delay\": " + stream_delay + ", " \
                    "\"resistance\": " + resistance + " }  ";
      Serial.println(response);              
    }
    
    if(!valid_request) {
      Serial.println("ERROR : unknown command");
    }
  }
}
