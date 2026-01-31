import pickle
import socket
import struct
import time
from threading import Thread

import cv2
import imutils
from pymavlink import mavutil
class Datas:
    def __init__(self,vehicle,heliport):
        self.gcs = None
        self.arm_ = None
        self.kamikaze = None
        self.konum=None
        self.vehicle = vehicle
        self.heliport = heliport
        # Socket Create
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_address = ("192.168.0.142", 5654)

        # Socket Bind
        self.server_socket.bind(self.socket_address)

        # Socket Listen
        self.server_socket.listen(2)

        Thread(target=self.telem_connect).start()

        Thread(target=self.heliport_location).start()


    def telem_connect(self):
        i = 0
        kamikaze_ip = "192.168.0.142"
        # Socket Accept
        while i < 2:
            client_socket, addr = self.server_socket.accept()
            if addr[0] == kamikaze_ip:
                self.kamikaze = client_socket
            else:
                self.gcs == client_socket
                Thread(target=self.gcs_camera).start()
                Thread(target=self.gcs_veri).start()
            i += 1
        self.gcs_camera()

    def gcs_camera(self):
        while True:
            vid = cv2.VideoCapture(0)
            while vid.isOpened():
                img, frame = vid.read()
                frame = imutils.resize(frame, width=320)
                a = pickle.dumps(frame)
                message = struct.pack("Q", len(a)) + a
                self.gcs.sendall(message)


    def gcs_veri(self):
        while True:
            message = self.vfr_hud()
            mission = self.next_mission()
            message = {"groundspeed":message.groundspeed,"airspeed":message.airspeed,"heading":message.heading,"next_wp":mission.seq,
                       "flightmode":self.flightmode(),"loc":self.location()}
            message = pickle.dumps(message)
            self.gcs.send(message)
            time.sleep(.5)
    
        
    def send_kamikaze(self,lat,lon):
        message = {"lat":lat,"lon":lon}
        message = pickle.dumps(message)
        self.kamikaze.send(message)
        time.sleep(0.5)
        return True
    
    def is_open(self,_open):# kapakların açılması/kapanması ile kamikazenin haberleşmesi
        if _open is True:
            self.kamikaze.send("True")
            while True:
                message = self.client_socket.recv(1024).decode()
                if message == "True":
                    break
            return True
        else:
            self.kamikaze.close()
            return True
        
    def heliport_location(self):
        self.konum = {None,None,None}
        self.hız=None
        self.heading=None
        while True:
            loc = self.heliport.location(False)
            loc = loc.split(",")
            for i,l in enumerate(loc):
                l.split("=")
                konum[i]=l[1]
            msg = self.heliport.recv_match(type="VFR_HUD", blocking=True)
            if msg is not None:
                heading = msg.heading
                hız = msg.groundspeed
                

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
    
    def kalan_yol(self):
        while True:
            msg = self.vehicle.recv_match(type='NAV_CONTROLLER_OUTPUT', blocking=True)
            if msg is not None:
                return msg.wp_dist
            
    def rakım(self,alt="yukseklik"):
        if alt == "yukseklik":
            while True:
                msg = self.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
                if msg is not None:
                    return msg.alt/1e3
        else:
            while True:
                msg = self.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
                if msg is not None:
                    return msg.relative_alt/1e3



