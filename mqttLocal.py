import time
import board
import busio
from digitalio import DigitalInOut
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_esp32spi.adafruit_esp32spi as esp
from adafruit_minimqtt import MQTT

# Configuration du réseau
esp32_cs = DigitalInOut(board.D9)
esp32_ready = DigitalInOut(board.D10)
esp32_reset = DigitalInOut(board.D5)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = esp.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

print("Connecting to AP...")
while not esp.is_connected:
    try:
        esp.connect_AP(b'MySSID', b'MyPassword')
    except RuntimeError as e:
        print("could not connect to AP, retrying: ",e)
        continue
print("Connected to", str(esp.ssid, 'utf-8'), "\tRSSI:", esp.rssi)

# Configuration du client MQTT
mqtt_broker = "172.16.5.101"  # Adresse IP de votre broker MQTT Mosquitto
mqtt_topic = "test"

# Configuration du client MQTT
mqtt_client = MQTT(socket, broker=mqtt_broker)

# Callback pour la réception des messages
def on_message(client, topic, message):
    print("Received message on topic {}: {}".format(topic, message))

# Connexion au broker MQTT
mqtt_client.on_message = on_message
mqtt_client.connect()

# Publication de messages
for i in range(5):
    print("Publishing message ", i)
    mqtt_client.publish(mqtt_topic, "Message {}".format(i))
    time.sleep(1)

# Abonnement à un topic
mqtt_client.subscribe(mqtt_topic)

while True:
    mqtt_client.loop()
    time.sleep(0.1)