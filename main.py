import board
import digitalio
import analogio
import time
import adafruit_bmp280
import adafruit_dht
import projet2
import wifi
from adafruit_motor.servo import Servo
import pwmio


# Mise en place des objets de la carte Arduino
i2c = board.I2C()
dht = adafruit_dht.DHT11(board.IO8)
dht2 = analogio.AnalogIn(board.A1)
led = digitalio.DigitalInOut(board.IO11)
led.direction = digitalio.Direction.OUTPUT

ecran = projet2.ecran()

# Init servo
pwm = pwmio.PWMOut(board.IO14)  
self = Servo(pwm)
self.value = True #True = fermé
self.angle = 0

# Init pump
pump = digitalio.DigitalInOut(board.IO13)
pump.switch_to_output(False)

# Init button
button = digitalio.DigitalInOut(board.IO9)
button.direction = digitalio.Direction.INPUT

# Init sensor eau
sensorEau = digitalio.DigitalInOut(board.IO12)
sensorEau.direction = digitalio.Direction.INPUT

# Init heater
heater = digitalio.DigitalInOut(board.IO10)
heater.switch_to_output(False)

# Init capteur température ambiante
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
bmp280.sea_level_pressure = 1016.10

# Init Fan
fan= digitalio.DigitalInOut(board.IO7)
fan.switch_to_output(False)

timerArrosage = 0
intervalleArrosage = time.monotonic() - 1800
last_time_recolte = 0
tableauHum = []
total = 0
hum_moyenne = 0


while True:
    # Led allume si il n'y a pu d'eau dans le réservoir
    led.value = not sensorEau.value
    
    # Gestion de la moyenne de l'humidité de la terre
    if(time.monotonic() - last_time_recolte > 1 ):
        #print(dht2.value)
        #print(sensorEau.value)
        print(dht.temperature)

        last_time_recolte = time.monotonic()
        humidite = dht2.value
     
        if len(tableauHum) < 60:
            tableauHum.append(humidite)
            total += humidite
        else:
            total -= tableauHum.pop(0)
            tableauHum.append(humidite)
            total += humidite

        hum_moyenne = total/len(tableauHum)
        print(hum_moyenne)

    #Activation de la pompe avec le bouton 
    if(button.value == True and pump.value == False and sensorEau.value == True):
        #print(pump.value)
        pump.value = True
        timerArrosage = time.monotonic()
    
    

    #Vérification de l'humidité 30 minutes après l'arrosage
    if(time.monotonic() - intervalleArrosage > 1800 and intervalleArrosage != 0 and sensorEau.value == True):
        #Activation de la pompe avec l'humidité de la terre
        if(hum_moyenne >= 50000):
            pump.value = True
            timerArrosage = time.monotonic()
            intervalleArrosage = 0
    
        # 17100 devrrait être arrosé
        # 16800 assez arrosé
        
       
    
    #La pompe arrose pendant 30 secondes
    if(time.monotonic()-timerArrosage >30 and timerArrosage != 0):
        pump.value = False
        intervalleArrosage = time.monotonic()
        timerArrosage = 0
        # Section sensor niveau d'eau
         
    # Section traitement du heater        
    
    if(dht.temperature <10):
        heater.value = True
    else:
        heater.value = False
    
    #print(dht.humidity) 
    
    if((dht.temperature >30 or dht.humidity >75) and fan.value == False):
        # ouvre la trap d'aération
        self.angle = 149
        # lance la fan
        fan.value = True
        print('Fan : True')
    elif ((dht.temperature <25 and dht.humidity <60) and fan.value == True) :
        self.angle = 0
        fan.value = False
            
        
    



    