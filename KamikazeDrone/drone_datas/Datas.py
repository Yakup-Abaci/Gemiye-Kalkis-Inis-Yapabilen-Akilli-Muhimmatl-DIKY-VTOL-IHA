import pickle
import socket
import struct
import time
from threading import Thread

import cv2
import imutils
from pymavlink import mavutil
class Datas:
    def __init__(self,vehicle):
        self.gcs = None
        self.vtol = None
        self.vehicle=vehicle
        Thread(target=self.vtol_connect).start()
        Thread(target=self.gcs_veri_connect).start()
        Thread(target=self.gcs_cam_connect).start()
        
    def gcs_cam_connect(self):
        gcs_ip="192.168.1.115"
        gcs_port=9997
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Socket will create with TCP and, IP protocols
        s.connect((gcs_ip, gcs_port))  # Will connect with the server
        
        self.gcs_camera(s)
       
    
    def gcs_veri_connect(self):
        gcs_ip="192.168.1.115"
        gcs_port=9998
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Socket will create with TCP and, IP protocols
        s.connect((gcs_ip, gcs_port))  # Will connect with the server
        
        Thread(target=self.gcs_camera,args=(s,)).start()
        self.gcs_veri(s)
        

    def vtol_connect(self):
        vtol_ip = "192.168.0.142"
        vtol_port = 9999
        
        self.vtol_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Socket will create with TCP and, IP protocols
        self.vtol_send.connect((vtol_ip, vtol_port))  # Will connect with the server

        
    def vtol_veri(self,al_ver):
        if al_ver == "al":
            msg = self.vtol_send.recv(1024)
            veri = pickle.loads(msg)
            return veri
        else:
            self.vtol_send.send("True")
            return True
           
    def gcs_camera(self,send):
        while True:
            vid = cv2.VideoCapture(0)
            while vid.isOpened():
                img, frame = vid.read()
                frame = imutils.resize(frame, width=320)
                a = pickle.dumps(frame)
                message = struct.pack("Q", len(a)) + a
                send.sendall(message)

    def gcs_veri(self,send):
        while True:
            message = self.vfr_hud()
            mission = self.next_mission()
            message = {"groundspeed":message.groundspeed,"airspeed":message.airspeed,"heading":message.heading,"next_wp":mission.seq,
                       "flightmode":self.flightmode(),"loc":self.location()}
            message = pickle.dumps(message)
            send.send(message)
            time.sleep(.5)
    

    def request_home_pos(self):
        self.vehicle.mav.command_long_send(0, 0, mavutil.mavlink.MAV_CMD_GET_HOME_POSITION, 0, 0, 0, 0, 0, 0, 0, 0)
        print(self.vehicle.recv_match(type="HOME_POSITION", blocking=True))

    def channels(self):
        while True:
            msg = self.vehicle.recv_match(type="RC_CHANNELS", blocking=True)
            if msg is not None:
                print(msg)

    def recv(self):
        # capability_msg = self.vehicle.mav.command_long_encode(0, 0, mavutil.mavlink.MAV_CMD_REQUEST_AUTOPILOT_CAPABILITIES, 0, 1, 0, 0, 0, 0, 0, 0)
        # self.vehicle.mav.send(capability_msg)
        # while True:
        #    msg = self.vehicle.recv_match(type="AUTOPILOT_VERSION")
        #    if msg is not None:
        #       capabilities = msg.capabilities
        # self.vehicle.mav.param_request_list_send(self.vehicle.target_system, self.vehicle.target_component) # parametre listesini mesaj olarak gönderir
        # self.vehicle.mav.mission_request_partial_list_send(self.vehicle.target_system, self.vehicle.target_component,0,-1)#MISSION_CURRENT
        # self.vehicle.waypoint_request_list_send() # mıssıon_count
        # self.vehicle.mav.mission_request_int_send(self.vehicle.target_system, self.vehicle.target_component,0) # Mıssıon_ıtem mesajı
        while True:
            ms = self.vehicle.recv_match()
            if ms is not None:
                print(ms)

    def vfr_hud(self):
        ms = self.vehicle.recv_match(type="VFR_HUD", blocking=True)
        if ms is not None:
            # print("airspeed=",ms.airspeed,"\ngroundspeed=",ms.groundspeed,"\nheading=",ms.heading,"\nthrottle=",ms.throttle,"\naltitude=",ms.alt,"\nclimb=",ms.climb)
            return ms

    def altitude(self):
        while True:
            ms = self.vehicle.recv_match(type="LOCAL_POSITION_NED", blocking=True)
            if ms is not None:
                return ms.z

    def next_mission(self):
        ms = self.vehicle.recv_match(type="MISSION_CURRENT", blocking=True)
        if ms is not None:
            return ms.seq
                        
    def flightmode(self):
        return self.vehicle.flightmode

    def arm(self):
        return self.vehicle.motors_armed()

    def location(self):
        return self.vehicle.location(True)

    def sys_status(self):
        msg = self.vehicle.recv_match(type="SYS_STATUS", blocking=True)
        bit = msg.onboard_control_sensors_health
        for i in range(31):
            deger = bit & 1
            print(mavutil.mavlink.enums["MAV_SYS_STATUS_SENSOR"][2 ** i].name,
                  mavutil.mavlink.enums["MAV_SYS_STATUS_SENSOR"][2 ** i].description,
                  deger)
            bit >>= 1
        print(msg.onboard_control_sensors_present,
              msg.onboard_control_sensors_enabled,
              msg.onboard_control_sensors_health)

    def get_params(self):
        self.vehicle.param_fetch_all()
        # while True:
        # msg = self.vehicle.recv_match(type='PARAM_VALUE', blocking=True)
        # if msg is not None:
        # print(f"param_id = {msg.param_id} param_value = {msg.param_value}")

    def get_param(self, param_name):
        try:
            self.vehicle.param_fetch_one(param_name.upper())
        except RuntimeError:
            return "Parametre hatalı"
        else:
            msg = self.vehicle.recv_match(type='PARAM_VALUE', blocking=True)
            return f"param_id = {msg.param_id} param_value = {msg.param_value}"



