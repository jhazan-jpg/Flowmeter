# Flowmeter
Micropython code for Raspberry Pi Pico W for use with an FS-3000AH flow meter. Publishes the volume of water that flows through the meter to an MQTT server using the Homie 3.0 convention.

The red wire on the flow meter needs to be connected to a 3.3V pin on the Pi Pico, black to GND and the brown (sensor) wire to GPIO 26. 
