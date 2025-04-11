# p1-boiler-dispatcher
Calculating export using P1 smartmeter protocol and adjusting consumption to avoid electricity overexport.

There are 3 threads
p1_state_reader.py - reading p1 state from text file. I'm using separate script that stores and updates P1 data to a file under tmpfs every second.
state_reader.py - reading boiler temperature from esp8266 with esphome and dallas termometer.
dispatcher.py - regulates boiler power based on temperature and solar production. Regulator is connected to esp8266 PWM pin.

It calculates average export for 15 minutes as it is a requirement for Lithuania. Can be easily updated to regulate power based on instant export power.
Will try to update and make it more flexible if I will have time for it.

Power and temperature limits can be adjusted in homeassistant.
Add following to configuration.yaml:

```yaml
input_number:
    max_export_to_grid_power_boiler:
        name: "Maximum allowed export to grid power by boiler"
        unit_of_measurement: "W"
        min: 9000
        max: 10000
    max_export_to_grid_power_boiler_buffer:
        name: "Buffer for maximum allowed export to grid power by boiler"
        unit_of_measurement: "W"
        min: 0
        max: 1000
    min_boiler_temperature:
        name: "Minimal boiler temperature"
        unit_of_measurement: "°C"
        min: 5
        max: 80
    min_boiler_temperature_morning:
        name: "Minimal boiler temperature in the morning"
        unit_of_measurement: "°C"
        min: 5
        max: 80
    min_boiler_temperature_evening:
        name: "Minimal boiler temperature in the evening"
        unit_of_measurement: "°C"
        min: 5
        max: 80
```
