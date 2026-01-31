from pymavlink import mavutil, mavwp
import os
import time
class arac:
    def __init__(self):
        os.environ['MAVLINK20'] = '1'
        mavutil.set_dialect("all")
        self.vehicle = mavutil.mavlink_connection('tcp:127.0.0.1:5762', baud=115200) #-> com değeri değişecek

    def veriler(self):
        while True:
                self.channels = self.vehicle.recv_match(type="RC_CHANNELS").to_dict()
                self.servo = self.vehicle.recv_match(type="SERVO_OUTPUT_RAW").to_dict()
                a=""
                for i in self.channels.keys():
                    if i.startswith("chan"):
                        a+=str(i)+"=>"+str(self.channels[i])+"\t"
                print("KANAL ÇIKTILARI\n",a)
                b=""
                for i in self.servo.keys():
                    if i.startswith("servo"):
                        b+=str(i)+"=>"+str(self.servo[i])+"\t"
                b+="\n"
                print("SERVO ÇIKTILARI\n",b)
                    
                time.sleep(3)
a=arac()
time.sleep(2)
a.veriler()
    

    