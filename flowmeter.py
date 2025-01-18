from machine import Pin
import time
import rp2
import network
import ubinascii
from machine import Pin
import urequests as requests
from secrets import secrets
import socket
from umqtt.robust import MQTTClient

pulse_count = 0
flow_frequency = 0
volume = 0
mqtt_host = 'HOSTNAME'
mqtt_client_id = 'pipico'

# Define blinking function for onboard LED to indicate error codes    
def blink_onboard_led(num_blinks):
    led = Pin('LED', Pin.OUT)
    for i in range(num_blinks):
        led.on()
        time.sleep(.2)
        led.off()
        time.sleep(.2)

blink_onboard_led(1)

# Set country to avoid possible errors
rp2.country('GB')

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# See the MAC address in the wireless chip OTP
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print('mac = ' + mac)

# Load login data from different file for safety reasons
ssid = secrets['ssid']
pw = secrets['pw']

wlan.connect(ssid, pw)

# Wait for connection with 10 second timeout
timeout = 30
while wlan.isconnected() == False:
    print('Waiting for connection...')
    time.sleep(1)
    blink_onboard_led(1)

def process_msg(topic, msg):
    global volume
    print(f'Topic: {topic}, Msg: {msg}')
    if topic == b'homie/flowsensor/sensor/volume':
        if volume == 0:
            vol = float(msg)
            print('Setting the volume')
            volume = vol
    elif topic == b'homie/flowsensor/sensor/reset/set' and msg == b'true':
        client.publish('homie/flowsensor/sensor/volume', '0', 1, True)
        client.publish('homie/flowsensor/sensor/reset', 'false', 1, True)
        print("Volume reset to 0")
        volume = 0
    return

if wlan.isconnected() == False:
    blink_onboard_led(2)
    raise RuntimeError('Wi-Fi connection failed')
else:
    blink_onboard_led(3)
    print('Connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])
    
try:
    client = MQTTClient(
        client_id = mqtt_client_id,
        server = mqtt_host,
        keepalive = 30)
except Exception as e:
    print('Error connecting to MQTT:', e)
    raise

HomieRoot = 'homie/flowsensor/'
client.set_last_will(HomieRoot + "$state", "lost", 1, True)
client.connect()
client.set_callback(process_msg)
client.subscribe('homie/flowsensor/sensor/volume')

client.subscribe('homie/flowsensor/sensor/reset/set')

mainRoot = f'{HomieRoot}sensor'
client.publish(HomieRoot + "$homie", "3.0", 1, True)
client.publish(HomieRoot+ "$name", "Flow Meter", 1, True)
client.publish(HomieRoot + "$state", "init", 1, True)

client.publish(f"{mainRoot}/$name", "Flow Meter", 1, True)
client.publish(f"{mainRoot}/$type", "FS-3000AH Flow Meter", 1, True)
client.publish(f"{mainRoot}/$properties", 'switch,volume,reset', 1, True)
switchNode = f'{mainRoot}/switch'
client.publish(f'{switchNode}/$name', 'Switch', 1, True)
client.publish(f'{switchNode}/$datatype', 'boolean', 1, True)
volumeNode = f'{mainRoot}/volume'
client.publish(f'{volumeNode}/$name', 'Volume', 1, True)
client.publish(f'{volumeNode}/$unit', 'l', 1, True)
client.publish(f'{volumeNode}/$datatype', 'float', 1, True)
resetNode = f'{mainRoot}/reset'
client.publish(f'{resetNode}/$name', 'Reset Volume Counter', 1, True)
client.publish(f'{resetNode}/$settable', 'true', 1, True)
client.publish(f'{resetNode}/$datatype', 'boolean', 1, True)

client.publish(HomieRoot + "$nodes", "sensor", 1, True)

client.publish(HomieRoot + "$state", "ready", 1, True)

sensorPin = Pin(26,Pin.IN,Pin.PULL_UP)
def callback(pin):
    global volume, flow_frequency, pulse_count
#    pulse_count = pulse_count + 1
    flow_frequency = flow_frequency + 1
#    print(pulse_count)
    if flow_frequency == 75: #750 pulses per litre
        volume = volume + 0.1
#        print(f'{volume} ml')
        client.publish(volumeNode, str(volume), 1, True)
        flow_frequency = 0
      
sensorPin.irq(trigger=Pin.IRQ_FALLING, handler=callback)

while True:
    if wlan.isconnected() == False:
        blink_onboard_led(2)
        wlan.connect(ssid, pw)
        time.sleep(10)
    else:
        client.check_msg()
        client.ping()
        time.sleep(30)
        blink_onboard_led(1)
