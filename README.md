# p1-boiler-dispatcher
Calculating export using P1 smartmeter protocol and adjusting consumption to avoid electricity overexport.

There are 3 threads
p1_state_reader.py - reading p1 state from text file. I'm using separate script that stores and updates P1 data to a file under tmpfs every second.
state_reader.py - reading boiler temperature from esp8266 with esphome and dallas termometer.
dispatcher.py - regulates boiler power based on temperature and solar production. Regulator is connected to esp8266 PWM pin.

It calculates average export for 15 minutes as it is a requirement for Lithuania. Can be easily updated to regulate power based on instant export power.
Will try to update and make it more flexible if I will have time for it.
