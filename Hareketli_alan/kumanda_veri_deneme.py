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
                self.channels = self.vehicle.recv_match(type="VFR_HUD",blocking=True)#.to_dict()
                if self.channels is not None:
                    print(self.channels.groundspeed)
                #self.servo = self.vehicle.recv_match(type="SERVO_OUTPUT_RAW",blocking=True)#.to_dict()
                """a=""
                for i in self.channels.keys():
                    if i.startswith("chan"):
                        a+=str(i)+"=>"+str(self.channels[i])+"\t"
                print("KANAL ÇIKTILARI\n",a)
                b=""
                for i in self.servo.keys():
                    if i.startswith("servo"):
                        b+=str(i)+"=>"+str(self.servo[i])+"\t"
                b+="\n"
                print("SERVO ÇIKTILARI\n",b)"""
                #print(self.channels)
                #print(self.servo)
                    
                #time.sleep(3)
    def set_servo(self, servo_number, pwm_value):
        """if not (1 <= servo_number <= 8):
            raise ValueError("Servo number must be between 1 and 8")
        if not (1000 <= pwm_value <= 2000):
            raise ValueError("PWM value must be between 1000 and 2000")"""

        self.vehicle.mav.command_long_send(
            self.vehicle.target_system,  # target_system
            self.vehicle.target_component,  # target_component
            mavutil.mavlink.MAV_CMD_DO_REPEAT_SERVO,  # command
            0,  # confirmation
            servo_number,  # param1: Servo number (1-8 for AUX channels 1-8)
            pwm_value,  # param2: PWM value (1000-2000)
            10, 1, 0, 0, 0  # param3 - param7: Unused
        )
    def set_rc(self):  # 3 sn
        self.vehicle.mav.rc_channels_override_send(self.vehicle.target_system, self.vehicle.target_component,
                                                   1100, 2000, 0, 1100, 0, 0, 0, 0)
    
    def location(self):
        return self.vehicle.location(False)

    def get_params(self):
        self.vehicle.param_fetch_all()
        while True:
            msg = self.vehicle.recv_match(type='PARAM_VALUE', blocking=True)
            if msg is not None:
                print(f"param_id = {msg.param_id} param_value = {msg.param_value}")
    def mesag(self):
        print(self.vehicle.messages)
a=arac()
a.mesag()
    

    