# Flowmeter
MicroPython code for Raspberry Pi Pico W for use with an FS-3000AH flow meter. Publishes the volume of water that flows through the meter to an MQTT server using the Homie 3.0 convention.

The red wire on the flow meter needs to be connected to a 3.3V pin on the Pi Pico, black to GND and the brown (sensor) wire to GPIO 26. 

The Pi will need umqtt.robust which depends on umqtt.simple.

A secrets.py files is required with the SSID and key for the WiFi.

The documentation for the flow meter has the following values for litres per pulse:

Flow rate (litres/min.)  Litres per pulse
0.6 – 1.0                 0.0039
1.0 – 2.5                 0.0040
2.5 – 8.0                 0.0041

My own measurements showed around 750 pulses per litre for the flow rates I'm using, so the Pi must be triggering on both rising and falling edges.
