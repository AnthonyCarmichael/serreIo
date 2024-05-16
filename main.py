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
#self.angle = 149
self.angle = 0

# Init pump

pump = digitalio.DigitalInOut(board.IO10)
pump.switch_to_output()

# Init button
button = digitalio.DigitalInOut(board.IO9)
button.direction = digitalio.Direction.INPUT

# Mise en place des objets de la carte Arduino
i2c = board.I2C()
dht = adafruit_dht.DHT11(board.IO8)
dht2 = analogio.AnalogIn(board.A0)
#pot = analogio.AnalogIn(board.A0)
led = digitalio.DigitalInOut(board.IO11)
led.direction = digitalio.Direction.OUTPUT

ecran = projet2.ecran()


# init timers
timer = time.monotonic()
timerReconnexion = time.monotonic()
timerEcran = time.monotonic()
timerAlert=time.monotonic()
timerArrosage = 0
timerEntreArrosage = 0
timerPublish = 0


alertHum = False
alertTemp = False
alert = False
cptFlash = 0
temp_actuelle=dht.temperature
humTerre = dht2.value


# récupère l'objet io depuis la fonction connecter_mqtt
#if wifi.radio.connected:
io = False


while True:
    if not wifi.radio.connected and time.monotonic() - timerReconnexion > 300:
        timerReconnexion = time.monotonic()
        #try:
            #io = projet2.connecter_mqtt()
        #except ConnectionError as e:
            #print(e)

    #print(humTerre)

    #print(time.monotonic()-timer)

    if(button.value == True and pump.value == False):
        pump.value = True
        print(pump.value)
        timerEntreArrosage = time.monotonic()
    
    if(humTerre < 20000 and pump.value == False and time.monotonic()-timerEntreArrosage >60):
        pump.value = True
        print(pump.value)
        timerEntreArrosage = time.monotonic()
    
    if(time.monotonic()-timerArrosage >5):
        timerArrosage = time.monotonic()
        pump.value = False
        print(pump.value)

    if(time.monotonic()-timerPublish > 60 and io != False):
        timerPublish = time.monotonic()
        io.publish('Temperature', temp_actuelle)
        print('envoi')
        
    if(time.monotonic() - timerEcran > 0.5):
        temp_actuelle=dht.temperature
        humTerre = dht2.value
        humidex=dht.humidity
        timerEcran = time.monotonic()
        ecran.rafraichir_texte("Température\nactuelle:{:.1f}C\nHumidité:{:.1f}".format(temp_actuelle,humidex))
        
    if(time.monotonic() - timer > 300):
        timer = time.monotonic()
        if wifi.radio.connected:
            
            try:
                io.loop()
            except (ValueError, RuntimeError) as e:
                print("Failed to get data, retrying\n", e)
                io.reconnect()
                continue


        
        # publish
        #data = {"temperature":temp_actuelle,"humidity":humidex}
        #io.publish("data",json.dumps(data))
        

    

    