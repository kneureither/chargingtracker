const int msg_len = 30;
const int pin_1 = 0;
const int pin_2 = 2;
const float resistance = 0.1;
const float restistance_corr_factor = 0.948;
float voltage_bridge = 1; //default value
char msg[msg_len];
float resistance_corr;
bool valid_request;

// delays in ms
int mean_delay = 50;
int stream_delay = 100;


void setup() {
  Serial.begin(9600);
  resistance_corr = resistance * restistance_corr_factor;
  delay(3000);
  voltage_bridge = (984+9970) / (float) 9970 * 4.92 / 5.24;
}


////Functions to read and calculate values +++++++++++++++++++++++

float ReadVoltageOnce(int pin) {
  float voltage_input = analogRead(pin) * voltage_bridge;
  return (voltage_input / (float) 1024) * 5.0;
}

float ReadCurrentDiffOnce(int pin_in, int pin_out) {
  float voltage_in = analogRead(pin_in) * voltage_bridge;
  float voltage_out = analogRead(pin_out) * voltage_bridge;
  float voltage = ((voltage_in - voltage_out) / (float) 1024) * 5.0;
  float my_current = voltage / resistance_corr;
  return my_current;
}

float ReadVoltageMean(int pin, int mean_count) {
  float voltage = 0;
  for(int i = 0; i < mean_count; i++) {
    voltage += ReadVoltageOnce(pin);
    delay(mean_delay);
  }
  return voltage / (float) mean_count;
}

float ReadCurrentDiffMean(int pin_in, int pin_out, int mean_count) {
  float current = 0;
  for(int i = 0; i < mean_count; i++) {
    current += ReadCurrentDiffOnce(pin_in, pin_out);
    delay(mean_delay);
  }
  return current / (float) mean_count;
}

////Functions to analyse serial input +++++++++++++++++++++++++++++++

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


////main()++++++++++++++++++++++++++++++++++++++++++

void loop() {
  valid_request = false;
  String response = "";
    
  if(Serial.available()) {
    Serial.readStringUntil('\n').toCharArray(msg, msg_len);
    String message = msg;
    
    if(strstr(msg, "V0?")) {
      valid_request = true;
      String command = getCommandString("V0?");
      int stream_count = ReadFlagValue(command, "-stream");
      int mean_count = ReadFlagValue(command, "-mean");

      if (stream_count == -1 && mean_count == -1) {
        float voltage = ReadVoltageOnce(pin_1);
        response = response + ("V0: " + String(voltage) + " ");
      }
      else if(stream_count != -1 && mean_count == -1) {
        for(int i = 0; i < stream_count; i++) {
          float voltage = ReadVoltageOnce(pin_1);
          Serial.println("V0: " + String(voltage) + " delay=" + stream_delay + " ");
          delay(stream_delay);
        }
      }
      else if(stream_count == -1 && mean_count != -1) {
        float voltage = ReadVoltageMean(pin_1, mean_count);
        response = response + ("V0: " + String(voltage) + " mean_count=" + mean_count + "delay=" + mean_delay + " ");
      } 
      else if(stream_count != -1 && mean_count != -1) {
        for(int i = 0; i < stream_count; i++) {
          float voltage = ReadVoltageMean(pin_1, mean_count);
          Serial.println("V0: " + String(voltage) + " mean_count=" + mean_count + "delay=" + mean_delay + " ");
          delay(stream_delay);
        }
      }
    } 
    if(strstr(msg, "V1?")) {
      valid_request = true;
      String command = getCommandString("V1?");
      int stream_count = ReadFlagValue(command, "-stream");
      int mean_count = ReadFlagValue(command, "-mean");

      if (stream_count == -1 && mean_count == -1) {
        float voltage = ReadVoltageOnce(pin_2);
        response = response + ("V1: " + String(voltage) + " ");
      }
      else if(stream_count != -1 && mean_count == -1) {
        for(int i = 0; i < stream_count; i++) {
          float voltage = ReadVoltageOnce(pin_2);
          Serial.println("V1: " + String(voltage) + " delay=" + stream_delay + " ");
          delay(stream_delay);
        }
      }
      else if(stream_count == -1 && mean_count != -1) {
        float voltage = ReadVoltageMean(pin_2, mean_count);
        response = response + ("V1: " + String(voltage) + " mean_count=" + mean_count + " delay=" + mean_delay + " ");
      } 
      else if(stream_count != -1 && mean_count != -1) {
        for(int i = 0; i < stream_count; i++) {
          float voltage = ReadVoltageMean(pin_2, mean_count);
          Serial.println("V1: " + String(voltage) + " mean_count=" + mean_count + " delay=" + mean_delay + " ");
          delay(stream_delay);
        }
      }
    }
    if(strstr(msg, "AD?")) {
      valid_request = true;
      String command = getCommandString("AD?");
      int stream_count = ReadFlagValue(command, "-stream");
      int mean_count = ReadFlagValue(command, "-mean");

      if (stream_count == -1 && mean_count == -1) {
        float current = ReadCurrentDiffOnce(pin_1, pin_2);
        response = response + ("AD: " + String(current) + " ");
      }
      else if(stream_count != -1 && mean_count == -1) {
        for(int i = 0; i < stream_count; i++) {
          float current = ReadCurrentDiffOnce(pin_1, pin_2);
          Serial.println("AD: " + String(current) + " delay=" + stream_delay + " ");
          delay(stream_delay);
        }
      }
      else if(stream_count == -1 && mean_count != -1) {
        float current = ReadCurrentDiffMean(pin_1, pin_2, mean_count);
        response = response + ("AD: " + String(current) + " mean_count=" + mean_count + " delay=" + mean_delay + " ");
      } 
      else if(stream_count != -1 && mean_count != -1) {
        for(int i = 0; i < stream_count; i++) {
          float current = ReadCurrentDiffMean(pin_1, pin_2, mean_count);
          Serial.println("AD: " + String(current) + " mean_count=" + mean_count + " delay=" + mean_delay + " ");
          delay(stream_delay);
        }
      }
    }
    
    //no data request but only status? request
    if(valid_request == false && strstr(msg, "Status?")) {
      valid_request = true;
      response = response + "{ " \
                        "\"mean delay\": " + mean_delay + ", " \
                        "\"stream delay\": " + stream_delay + ", " \
                        "\"resistance\": " + resistance + ", " \
                        "\"bridge\": " + voltage_bridge + " }";
      //Serial.println(response);              
    }
    
    if(!valid_request) {
      Serial.println("ERROR : unknown command:" + message);
    }
    else {
      Serial.println(response);
    }
  }
}
