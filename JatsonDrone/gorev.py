from drone_codes.Drone import Drone
from drone_data.Datas import Datas
from image_processing.CameraVision import CameraVision
from hareketli_alan.Alan import Hareketli_alan
import time
class Gorev:
    def __init__(self):
        self.drone = Drone()
        self.data = Datas(self.drone.vehicle,self.drone.heliport)
        self.camera=CameraVision(self.drone)
        self.hareketli_alan = Hareketli_alan()
    
    def baslat(self):
        self.camera.start()
        self.drone.vehicle_mode = "GUIDED"
        time.sleep(0.2)
        self.drone.arm_drone = True
        self.drone.upload_mission("waypoint_files/yollar.txt")
        time.sleep(0.2)
        
    def kontrol(self):
        while True:
            if self.camera.hedef_find == True:
                self.data.send_kamikaze(self.camera.find_lat,self.camera.find_lon)
                if self.data.is_open(self.drone.set_servo_angle_servokit(17,120)):#kapağın açılması
                    if self.data.is_open(self.drone.set_servo_angle_servokit(5,90)):#aracı tutan kolun açılması
                        self.drone.set_servo_angle_servokit(17,0)#kapağın kapanması
                        break

        Thread(target=self.drone.kamera_dondur()).start
        self.camera.change_model("heliport")
        while True:
            alan_konum = self.hareketli_alan.location()
            if int(self.data.rakım("yukseklik"))>12:
                self.drone.reposition(alan_konum[0],alan_konum[1],self.data.rakım("rakım")-10)
            
            else:
                if self.camera.heliport_find:
                    if int(self.data.rakım("yukseklik"))>2:
                        self.drone.reposition(alan_konum[0],alan_konum[1],,self.data.rakım("rakım")-self.data.rakım("yukseklik")+2)
                    
                    else:
                        if self.kamera.arac_konum == 1:
                            self.drone.move(self.hareketli_alan.hız()+1,self.hareketli_alan.hız()-1,0)
                        elif self.kamera.arac_konum == 2:
                            self.drone.move(self.hareketli_alan.hız()+1,self.hareketli_alan.hız(),0)
                        elif self.kamera.arac_konum == 3:
                            self.drone.move(self.hareketli_alan.hız()+1,self.hareketli_alan.hız()+1,0)
                        elif self.kamera.arac_konum == 4:
                            self.drone.move(self.hareketli_alan.hız(),self.hareketli_alan.hız()-1,0)
                        elif self.kamera.arac_konum == 5:
                            # MESAFE SENSÖRÜNDEN VERİ OKUMA YAPILMASI GEREKİYOR
                        elif self.kamera.arac_konum == 6:
                            self.drone.move(self.hareketli_alan.hız(),self.hareketli_alan.hız()+1,0)
                        elif self.kamera.arac_konum == 7:
                            self.drone.move(self.hareketli_alan.hız()-1,self.hareketli_alan.hız()-1,0)
                        elif self.kamera.arac_konum == 8:
                            self.drone.move(self.hareketli_alan.hız()-1,self.hareketli_alan.hız(),0)
                        else:
                            self.drone.move(self.hareketli_alan.hız()-1,self.hareketli_alan.hız()+1,0)
                        
                 
                
gorev = Gorev()
gorev.baslat()
gorev.kontrol()