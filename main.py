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


def updateHumTerreMin(client, topic, message):
    global settingHumTerreMin
    # Method called whenever user/feeds has a new value
    print("New message on topic {0}: {1} ".format(topic, message))
    settingHumTerreMin = int(message)

def updateTempMin(client, topic, message):
    global settingTempMin
    # Method called whenever user/feeds has a new value
    print("New message on topic {0}: {1} ".format(topic, message))
    settingTempMin = int(message)
    
def updateTempMax(client, topic, message):
    global settingTempMax
    # Method called whenever user/feeds has a new value
    print("New message on topic {0}: {1} ".format(topic, message))
    settingTempMax = int(message)
    
def updateArroMin(client, topic, message):
    global settingArroMin
    # Method called whenever user/feeds has a new value
    print("New message on topic {0}: {1} ".format(topic, message))
    settingArroMin = int(message)
    
def updateArroMax(client, topic, message):
    global settingArroMax
    # Method called whenever user/feeds has a new value
    print("New message on topic {0}: {1} ".format(topic, message))
    settingArroMax = int(message)
    
def updateHumAirMax(client, topic, message):
    global settingHumAirMax
    # Method called whenever user/feeds has a new value
    print("New message on topic {0}: {1} ".format(topic, message))
    settingHumAirMax = int(message)

def controlFan(client, topic, message):
    global fan
    global servo
    # Method called whenever user/feeds has a new value
    print("New message on topic {0}: {1} ".format(topic, message))
    if message == "0":
        fan.value = False
        servo.angle = 0
    elif message == "1":
        fan.value = True
        servo.angle = 149
    
def controlHeater(client, topic, message):
    global heater
    # Method called whenever user/feeds has a new value
    print("New message on topic {0}: {1} ".format(topic, message))
    if message == "0":
        heater.value = False
    elif message == "1":
        heater.value = True

def gestionAuto(client, topic, message):
    global settingAuto
    # Method called whenever user/feeds has a new value
    print("New message on topic {0}: {1} ".format(topic, message))
    if message == "0":
        settingAuto = False
    elif message == "1":
        settingAuto = True
        
def arrosage(client, topic, message):
    global pump
    global timerArrosage
    
    # Method called whenever user/feeds has a new value
    print("New message on topic {0}: {1} ".format(topic, message))
    pump.value = True
    timerArrosage = time.monotonic()
    if(time.monotonic()-timerArrosage >30 and timerArrosage != 0):
            pump.value = False
            timerArrosage = 0



# Mise en place des objets de la carte Arduino
i2c = board.I2C()
dht = adafruit_dht.DHT11(board.IO8)
dht2 = analogio.AnalogIn(board.A1)
led = digitalio.DigitalInOut(board.IO11)
led.direction = digitalio.Direction.OUTPUT

ecran = projet2.ecran()
timer500ms = time.monotonic()

# settings
settingHumTerreMin=50000
settingTempMin = 10
settingTempMax = 30
settingArroMin = 10
settingArroMax = 60
settingHumAirMax = 75

settingAuto = True


# Init servo
pwm = pwmio.PWMOut(board.IO14)  
servo = Servo(pwm)
servo.value = True #True = fermé
servo.angle = 0

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

timerEnvoi = 0
timerArrosage = 0
intervalleArrosage = time.monotonic() - 1800
last_time_recolte = 0
tableauHum = []
total = 0
hum_moyenne = 0

# Gestion linéaire d'arrosage
tempReelArrosage =0

io = projet2.connecter_mqtt()

# Subscribe pour les settings
if io !=False:
    io.subscribe("newSettingHumTerreMin")
    io.add_feed_callback("newSettingHumTerreMin", updateHumTerreMin)
    io.subscribe("newSettingTempMin")
    io.add_feed_callback("newSettingTempMin", updateTempMin)
    io.subscribe("newSettingTempMax")
    io.add_feed_callback("newSettingTempMax", updateTempMax)
    io.subscribe("newSettingArroMin")
    io.add_feed_callback("newSettingArroMin", updateArroMin)
    io.subscribe("newSettingArroMax")
    io.add_feed_callback("newSettingArroMax", updateArroMax)
    io.subscribe("newSettingHumAirMax")
    io.add_feed_callback("newSettingHumAirMax", updateHumAirMax)
    io.subscribe("controlFan")
    io.add_feed_callback("controlFan", controlFan)
    io.subscribe("controlHeater")
    io.add_feed_callback("controlHeater", controlHeater)
    io.subscribe("auto")
    io.add_feed_callback("auto", gestionAuto)
    io.subscribe("arrosage")
    io.add_feed_callback("arrosage", arrosage)


while True:
    io.loop()
     # Affichage à toute les 0.5 secondes de l'écran
    if(time.monotonic()-timer500ms>0.5):
        if(settingAuto):
            auto='A'
        else:
            auto='M'
        if(fan.value):
            valueFan="ON"
        else:
            valueFan='OFF'
        if(sensorEau.value):
            sensor="Plein"
        else:
            sensor='Vide'
        if(heater.value):
            heat="On"
        else:
            heat='Off'
        if(io == False):
            connect="Déco"
        else:
            connect='Co'
        ecran.rafraichir_texte("A/M: "+auto+" MQTT: "+ connect + "\nFan: "+valueFan + " Eau: " + sensor + "\nHT:{:.1f} Heat: ".format(dht2.value) + heat + "\nHA:{:.1f} T:{:.1f}".format(dht.humidity,dht.temperature))
        timer500ms = time.monotonic()
    if time.monotonic() - timerEnvoi > 10:
        if  io !=False:
            io.publish("Temperature", dht.temperature)
            io.publish("HumTerre", dht2.value)  
            io.publish("HumAir", dht.humidity)
            if fan.value == True:
                io.publish("fan", "true")
            else:
                io.publish("fan", "false")
            if heater.value == True:
                io.publish("heater", "true")
            else:
                io.publish("heater", "false")
            if sensorEau.value == True:
                io.publish("sensorEau", "true")
            else:
                io.publish("sensorEau", "false")
                
            # publish pour les settings
            io.publish("settingHumTerreMin",settingHumTerreMin)
            io.publish("settingTempMin",settingTempMin)
            io.publish("settingTempMax",settingTempMax)
            io.publish("settingArroMin",settingArroMin)
            io.publish("settingArroMax",settingArroMax)
            io.publish("settingHumAirMax",settingHumAirMax)
            print(settingHumTerreMin)
            print(settingTempMin)
            print(settingTempMax)
            print(settingArroMin)
            print(settingArroMax)
            print(settingHumAirMax)
        else:
            print("Envoi de données impossible! Tentative de connexion avec le serveur MQTT")
            io = projet2.connecter_mqtt()
            if io != False:
                io.subscribe("newSettingHumTerreMin")
                io.add_feed_callback("newSettingHumTerreMin", updateHumTerreMin)
                io.subscribe("newSettingTempMin")
                io.add_feed_callback("newSettingTempMin", updateTempMin)
                io.subscribe("newSettingTempMax")
                io.add_feed_callback("newSettingTempMax", updateTempMax)
                io.subscribe("newSettingArroMin")
                io.add_feed_callback("newSettingArroMin", updateArroMin)
                io.subscribe("newSettingArroMax")
                io.add_feed_callback("newSettingArroMax", updateArroMax)
                io.subscribe("newSettingHumAirMax")
                io.add_feed_callback("newSettingHumAirMax", updateHumAirMax)
                io.subscribe("controlFan")
                io.add_feed_callback("controlFan", controlFan)
                io.subscribe("controlHeater")
                io.add_feed_callback("controlHeater", controlHeater)
                io.subscribe("auto")
                io.add_feed_callback("auto", gestionAuto)
                io.subscribe("arrosage")
                io.add_feed_callback("arrosage", arrosage)    
                 
        timerEnvoi = time.monotonic()
    # Led allume si il n'y a pu d'eau dans le réservoir
    led.value = not sensorEau.value
    if settingAuto:
        # Gestion de la moyenne de l'humidité de la terre
        if(time.monotonic() - last_time_recolte > 1 ):
            #print(dht2.value)
            #print(sensorEau.value)
            #print(dht.temperature)
            #print(hum_moyenne)

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
            

        #Activation de la pompe avec le bouton 
        if(button.value == True and pump.value == False and sensorEau.value == True):
            percent =(dht2.value - 50000)* 100/1216 
        
            tempReelArrosage= settingArroMax*percent/100
            
            if tempReelArrosage < settingTempMin:
                tempReelArrosage = settingTempMin
            
            # Arrosage
            pump.value = True
            timerArrosage = time.monotonic()
            intervalleArrosage = 0
            print(tempReelArrosage)
        
        

        #Vérification de l'humidité 30 minutes après l'arrosage
        if(time.monotonic() - intervalleArrosage > 1800 and intervalleArrosage != 0 and sensorEau.value == True):
            #Activation de la pompe avec l'humidité de la terre
            if(hum_moyenne > settingHumTerreMin):
                # Gestion linéaire d'arrosage
                percent =(dht2.value - settingHumTerreMin)* 100/1216 
                
                tempReelArrosage= settingArroMax*percent/100
                
                if tempReelArrosage < settingArroMin:
                    tempReelArrosage = settingArroMin
                
                # Arrosage
                pump.value = True
                timerArrosage = time.monotonic()
                intervalleArrosage = 0
                print(tempReelArrosage)
        
            # 17100 devrrait être arrosé
            # 16800 assez arrosé
            
        
        #La pompe arrose pendant 30 secondes
        if(time.monotonic()-timerArrosage >tempReelArrosage and timerArrosage != 0):
            pump.value = False
            intervalleArrosage = time.monotonic()
            timerArrosage = 0
            # Section sensor niveau d'eau
            
        # Section traitement du heater        
        
        if(dht.temperature <settingTempMin):
            heater.value = True
        else:
            heater.value = False
        
        #print(dht.humidity) 
        
        if((dht.temperature >settingTempMax or dht.humidity >settingHumAirMax) and fan.value == False):
            # ouvre la trap d'aération
            servo.angle = 149
            # lance la fan
            fan.value = True
            print('Fan : True')
        elif ((dht.temperature <settingTempMax-5 and dht.humidity <settingHumAirMax-5) and fan.value == True) :
            servo.angle = 0
            fan.value = False
                
        
    



    