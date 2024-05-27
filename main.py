import board
import digitalio
import analogio
import time
#import adafruit_bmp280
import adafruit_dht
import projet2
import wifi
from adafruit_motor.servo import Servo
import pwmio

# Init servo
pwm = pwmio.PWMOut(board.IO14)  
self = Servo(pwm)
self.value = True #True = fermé
self.angle = 149
#self.angle = 0

# Init pump

pump = digitalio.DigitalInOut(board.IO13)
pump.switch_to_output(False)

# Init button
button = digitalio.DigitalInOut(board.IO9)
button.direction = digitalio.Direction.INPUT

# Mise en place des objets de la carte Arduino
i2c = board.I2C()
dht = adafruit_dht.DHT11(board.IO8)
dht2 = analogio.AnalogIn(board.A0)
led = digitalio.DigitalInOut(board.IO11)
led.direction = digitalio.Direction.OUTPUT

ecran = projet2.ecran()
timerArrosage = 0
timer = 0
last_time_recolte = 0
tableauHum = []
total = 0
hum_moyenne = 0
while True:

    # Gestion de la moyenne de l'humidité de la terre
    if(time.monotonic() - last_time_recolte > 1):

        last_time_recolte = time.monotonic()
        humidite = dht2.value
     
        if len(tableauHum) < 120:
            tableauHum.append(humidite)
            total += humidite
        else:
            total -= tableauHum.pop(0)
            tableauHum.append(humidite)
            total += humidite

        hum_moyenne = total/len(tableauHum)
        print(hum_moyenne)

    #Activation de la pompe avec le bouton 
    if(button.value == True and pump.value == False):
        print(pump.value)
        pump.value = True
        timerArrosage = time.monotonic()
    
    #La pompe arrose pendant 30 secondes
    if(time.monotonic()-timerArrosage >30):
        pump.value = False

    #Activation de la pompe avec l'humidité de la terre
    if(hum_moyenne >= 17000):
        pump.value = True
        timerArrosage = time.monotonic()
    
        # 17098 devrrait être arrosé
        # 16800 assez arrosé

    