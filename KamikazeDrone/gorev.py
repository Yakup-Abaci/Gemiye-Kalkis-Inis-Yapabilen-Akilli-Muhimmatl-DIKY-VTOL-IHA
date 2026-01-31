from pymavlink import mavutil
from drone_codes.KamikazeDrone import KamikazeDrone
from  drone_datas.Datas import Datas
import RPi.GPIO as GPIO
from threading import Thread
import time
class Gorev:
    def __init__(self):
        self.vehicle = KamikazeDrone()
        self.data = Datas()
        self.inis=False
        self.rudder = self.servo("rudder")
        self.eleron = self.servo("elevator")
        self.elevator = self.servo("eleron")
        self.t1 = Thread(target=self.eleron_ac)
        self.t2 = Thread(target=self.elevator_ac)
        self.t3 = Thread(target=self.rudder_ac)
        self.start = False
        self.gidis_konumu = [-35,149,30]#lat,lon,alt
        Thread(target=self.sabit_durus).start()
        
    def servo(self,parca):
        if parca == "eleron":
            PIN = 17
        elif parca == "elevator":
            PIN = 15
        else:
            PIN = 12
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(servoPIN, GPIO.OUT)

        pwm = GPIO.PWM(PIN, 330) 
        pwm.start(0)
        
        return pwm
    
    def eleron_ac(self):#servonun dönüş açısı lazım
        x=((1/180)*90 + 1)*33
        self.eleron.ChangeDutyCycle(x)
        self.eleron.stop()
    
    def rudder_ac(self):
        x=((1/180)*90 + 1)*33
        self.rudder.ChangeDutyCycle(x)
        self.rudder.stop()
        
    def elevator_ac(self):
        x=((1/180)*90 + 1)*33
        self.elevator.ChangeDutyCycle(x)
        self.elevator.stop()
        
    def sabit_durus(self):
        while True:
            if not self.start:
                self.vehicle.set_rc()
            else:
                break
            time.sleep(1)
    
    def gorev(self):
        while True:
            veri = self.data.vtol_veri("al")
            if type(veri) == str:
                if not self.inis:
                    yukseklik = self.data.altitude()
                    self.data.vtol_veri("ver")
                    self.inis=True 
                if self.data.altitude() - yukseklik > 2:
                    self.data.vtol_veri("ver")
                    self.t1.start()
                    self.t1.join()
                    self.t2.start()
                    self.t2.join()
                    self.t3start()
                    self.t3.join()
                    self.vehicle.arm_drone(1)
                    self.vehicle.takeoff(1)
                    self.vehicle.set_auto()
                    break
                
            elif type(veri) == dict:
                iniş_yuksekligi = 5
                self.vehicle.add_location("waypoint",veri["lat"],veri["lon"],iniş_yuksekligi)
                self.vehicle.add_location("waypoint",self.gidis_konumu[0],self.gidis_konumu[1],self.gidis_konumu[2])
                continue
            
        while True :
            if self.vehicle.next_mission() == 2:
                if self.vehicle.channels.chan9_raw > 0:
                    self.vehicle.close_connection()
                    break
        

            
                