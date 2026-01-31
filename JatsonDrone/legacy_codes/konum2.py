import cv2
import imutils
import math
<<<<<<< HEAD:konum2.py
=======
import pickle
import socket
import struct
import time
from threading import Thread

import numpy as np
from pymavlink import mavutil, mavwp

>>>>>>> erdal.nayir:legacy_codes/konum2.py

class Drone:
    def __init__(self):
        self.__arm_drone = None
        self.vehicle = mavutil.mavlink_connection('tcp:127.0.0.1:5762', baud=115200)
        mavutil.set_dialect("ardupilotmega")
        # self.vehicle_mode = None
        # self.arm_drone = None
        # self.param = None
        self.waypoint_loader = mavwp.MAVWPLoader(self.vehicle.target_system, self.vehicle.target_component)
        self.vehicle.wait_heartbeat()
        self.gorev = False

    def send_heartbeat(self):
        self.vehicle.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_VTOL_TILTROTOR,
                                        mavutil.mavlink.MAV_AUTOPILOT_GENERIC,
                                        8,
                                        16,
                                        0,
                                        0)
        msg = self.vehicle.recv_match(type='HEARTBEAT', blocking=True)
        print(msg)

    def multi_copter_to_fixed_wing(self, mode):
        if mode == 'drone':
            mode = mavutil.mavlink.MAV_VTOL_STATE_MC
        else:
            mode = mavutil.mavlink.MAV_VTOL_STATE_FW
        self.vehicle.mav.command_long_send(
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_CMD_DO_VTOL_TRANSITION,
            0,
            mode,
            0,
            0,
            0,
            0,
            0,
            0)
        print(self.vehicle.recv_match(type="COMMAND_ACK", blocking=True))

    @property
    def vehicle_mode(self):
        while True:
            msg = self.vehicle.recv_match(type="HEARTBEAT")
            if msg is not None and msg.type != 6:
                break
        return self.vehicle.flightmode

    @vehicle_mode.setter
    def vehicle_mode(self, mode):
        if mode.upper() in mavutil.mode_mapping_apm.values():
            for key, value in mavutil.mode_mapping_apm.items():
                if value == mode.upper():
                    self.vehicle.flightmode = self.vehicle.set_mode_apm(key)
        else:
            self.vehicle.flightmode = self.vehicle.flightmode

    @property
    def arm_drone(self):
        self.__arm_drone = self.vehicle.motors_armed()
        return True if self.__arm_drone else False

    @arm_drone.setter
    def arm_drone(self, arm):
        while True:
            msg = self.vehicle.recv_match(type="SYS_STATUS", blocking=True).onboard_control_sensors_health
            msg >>= 28
            if msg & 1 == 1:
                break
        if arm:
            self.vehicle.arducopter_arm()
            self.vehicle.motors_armed_wait()
            self.__arm_drone = True
        else:
            self.vehicle.arducopter_disarm()
            self.vehicle.motors_disarmed_wait()
            self.__arm_drone = False

    def takeoff(self, altitude):
        self.vehicle.mav.command_long_send(
            self.vehicle.target_system,  # target_system
            self.vehicle.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,  # command
            0,  # confirmation
            0,  # param1 (1 to indicate arm)
            0,  # param2 (all other params meaningless)
            0,  # param3
            0,  # param4
            0,  # param5
            0,  # param6
            altitude)  # param7
        while True:
            if self.vehicle.recv_match(type="GLOBAL_POSITION_INT",
                                       blocking=True).relative_alt * 0.001 > altitude * 0.95:
                print("yüksekliğe ulaşıldı")
                break
            else:
                print("yükseklik",
                      self.vehicle.recv_match(type="GLOBAL_POSITION_INT", blocking=True).relative_alt * 0.001)

    def change_alt(self, altitude):
        if altitude > 0:
            çarpan = 1
        else:
            çarpan = -1
        location = self.vehicle.recv_match(type="POSITION_TARGET_GLOBAL_INT", blocking=True).alt
        self.vehicle.mav.set_position_target_global_int_send(
            time_boot_ms=0,
            target_system=self.vehicle.target_system,
            target_component=self.vehicle.target_component,
            coordinate_frame=mavutil.mavlink.MAV_FRAME_GLOBAL_INT,
            type_mask=0b00000111000111,
            lat_int=0,
            lon_int=0,
            alt=location + altitude,
            vx=0,
            vy=0,
            vz=0,
            afx=0,
            afy=0,
            afz=0,
            yaw=0,
            yaw_rate=0
        )
        time.sleep(1)
        hedef = self.vehicle.recv_match(type="POSITION_TARGET_GLOBAL_INT", blocking=True).alt - location
        while True:
            yukseklik = self.vehicle.recv_match(type="GLOBAL_POSITION_INT", blocking=True).relative_alt / 1000.0
            print(hedef)
            if yukseklik * çarpan > hedef * 0.95 * çarpan:
                print("hedefe ulaşıldı")
                break
            else:
                print("yükseklik ", yukseklik)

    def move(self, ileri, yan, dikey):
        # location = self.vehicle.recv_match(type="POSITION_TARGET_LOCAL_NED",blocking=True)
        self.vehicle.mav.set_position_target_local_ned_send(
            time_boot_ms=0,
            target_system=self.vehicle.target_system,
            target_component=self.vehicle.target_component,
            coordinate_frame=mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            type_mask=0b110111000111,  # 0b00001111000111,0b110111000111
            x=0, y=0, z=0,
            vx=ileri,
            vy=yan,
            vz=dikey,
            afx=0, afy=0, afz=0, yaw=0, yaw_rate=0)

    def cmd_set_home(self, home_location, altitude):
        print('--- ', self.vehicle.target_system, ',', self.vehicle.target_component)
        self.vehicle.mav.command_long_send(
            self.vehicle.target_system, self.vehicle.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_HOME,
            1,  # set position
            0,  # param1
            0,  # param2
            0,  # param3
            0,  # param4
            home_location[0],  # lat
            home_location[1],  # lon
            altitude)

    def upload_mission(self, filename):
        home_location = None
        home_altitude = None

        with open(filename) as f:
            for i, line in enumerate(f):
                if i == 0:
                    if not line.startswith('QGC WPL 110'):
                        raise Exception('File is not supported WP version')
                else:
                    line_array = line.split('\t')
                    ln_seq = int(line_array[0])
                    ln_current = int(line_array[1])
                    ln_frame = int(line_array[2])
                    ln_command = int(line_array[3])
                    ln_param1 = float(line_array[4])
                    ln_param2 = float(line_array[5])
                    ln_param3 = float(line_array[6])
                    ln_param4 = float(line_array[7])
                    ln_x = float(line_array[8])
                    ln_y = float(line_array[9])
                    ln_z = float(line_array[10])
                    ln_auto_continue = int(float(line_array[11].strip()))
                    if i == 1:
                        home_location = (ln_x, ln_y)
                        home_altitude = ln_z
                    p = mavutil.mavlink.MAVLink_mission_item_message(self.vehicle.target_system,
                                                                     self.vehicle.target_component,
                                                                     ln_seq, ln_frame,
                                                                     ln_command,
                                                                     ln_current, ln_auto_continue, ln_param1, ln_param2,
                                                                     ln_param3, ln_param4, ln_x, ln_y, ln_z)
                    self.waypoint_loader.add(p)

        if not self.gorev:
            self.cmd_set_home(home_location, home_altitude)
            self.gorev = True
        msg = self.vehicle.recv_match(type=['COMMAND_ACK'], blocking=True)
        print(msg)
        print('Set home location: {0} {1}'.format(home_location[0], home_location[1]))
        time.sleep(1)

        # send waypoint to airframe
        self.vehicle.waypoint_clear_all_send()
        self.vehicle.waypoint_count_send(self.waypoint_loader.count())

        for i in range(self.waypoint_loader.count()):
            msg = self.vehicle.recv_match(type=['MISSION_REQUEST'], blocking=True)
            print(msg)
            self.vehicle.mav.send(self.waypoint_loader.wp(msg.seq))
            print('Sending waypoint {0}'.format(msg.seq))

    def add_mission(self, komut, lat, long, alt):
        mission_cmds = {"takeoff": mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
                        "waypoint": mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                        "rtl": mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
                        "land": mavutil.mavlink.MAV_CMD_NAV_LAND,
                        "loiter": mavutil.mavlink.MAV_CMD_NAV_LOITER_UNLIM}
        command = mission_cmds[komut] if komut in mission_cmds else 0
        p = mavutil.mavlink.MAVLink_mission_item_message(self.vehicle.target_system,
                                                         self.vehicle.target_component,
                                                         0, mavutil.mavlink.MAV_FRAME_GLOBAL_TERRAIN_ALT,
                                                         command,
                                                         0, 0, 0, 0, 0, 0,
                                                         lat, long, alt)
        if not self.gorev:
            self.waypoint_loader.add(p)
            self.gorev = True

        self.waypoint_loader.add(p)
        self.vehicle.waypoint_count_send(self.waypoint_loader.count())

        for i in range(self.waypoint_loader.count()):
            self.vehicle.mav.send(self.waypoint_loader.wp(p))
            print('Sending waypoint {0}'.format(p))

    def close_connection(self):
        self.vehicle.close()

    def set_rc(self):  # 3 sn
        self.vehicle.mav.rc_channels_override_send(self.vehicle.target_system, self.vehicle.target_component,
                                                   0, 2000, 0, 0, 0, 0, 0, 0)

    def send_attitude(self):
        self.vehicle.mav.set_attitude_target_send(0, self.vehicle.target_system, self.vehicle.target_component,
                                                  mavutil.mavlink.ATTITUDE_TARGET_TYPEMASK_BODY_YAW_RATE_IGNORE,
                                                  [1, 1, 1, 1], 0.0, 0.0, 50, 10)

    def reposition(self):
        self.vehicle.mav.command_long_send(0, 0, mavutil.mavlink.MAV_CMD_GET_HOME_POSITION, 0, 0, 0, 0, 0, 0, 0, 0)
        alt = self.vehicle.recv_match(type="HOME_POSITION", blocking=True).altitude / 1e3

        lat = int(-35.35628801 * 1e7)
        lon = int(149.16105665 * 1e7)
        self.vehicle.mav.command_int_send(self.vehicle.target_system, self.vehicle.target_component,
                                          mavutil.mavlink.MAV_FRAME_GLOBAL,
                                          mavutil.mavlink.MAV_CMD_DO_REPOSITION, 0, 0,
                                          1, 1, 1, 0, lat, lon, alt + 25)
        print(self.vehicle.recv_match(type="COMMAND_ACK", blocking=True))

    def motor_test(self):
        self.vehicle.mav.command_long_send(self.vehicle.target_system, self.vehicle.target_component,
                                           mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST, 0, 1,
                                           mavutil.mavlink.MOTOR_TEST_THROTTLE_PWM,
                                           2000, 5, 4, mavutil.mavlink.MOTOR_TEST_ORDER_BOARD, 0)
        print(self.vehicle.recv_match(type="COMMAND_ACK", blocking=True))

    def goto(self):  # sadece yükseklik dğeiştiriyor
        self.vehicle.mav.command_long_send(0, 0, mavutil.mavlink.MAV_CMD_GET_HOME_POSITION, 0, 0, 0, 0, 0, 0, 0, 0)
        alt = self.vehicle.recv_match(type="HOME_POSITION", blocking=True).altitude / 1e3

        self.vehicle.mav.set_position_target_global_int_send(time_boot_ms=0, target_system=self.vehicle.target_system,
                                                             target_component=self.vehicle.target_component,
                                                             coordinate_frame=mavutil.mavlink.MAV_FRAME_GLOBAL_INT,
                                                             type_mask=0b110000000000,
                                                             lat_int=int(-35.35989877 * 1e7),
                                                             lon_int=int(149.15884370 * 1e7), alt=alt + 50,
                                                             vx=0, vy=0, vz=0, afx=0, afy=0, afz=0, yaw=0, yaw_rate=0)

    def change_yaw(self):
        self.vehicle.mav.command_int_send(self.vehicle.target_system, self.vehicle.target_component,
                                          mavutil.mavlink.MAV_FRAME_LOCAL_NED,
                                          mavutil.mavlink.MAV_CMD_GUIDED_CHANGE_HEADING, 0, 0,
                                          mavutil.mavlink.HEADING_TYPE_COURSE_OVER_GROUND, 10, 5, 0, 0, 0, 0)
        print(self.vehicle.recv_match(type="COMMAND_ACK", blocking=True))

<<<<<<< HEAD:konum2.py
class veriler:
    def __init__(self,arac):
=======

class Veriler:
    def __init__(self, arac):
        self.gcs = None
        self.arm_ = None
        self.kamikaze = None
>>>>>>> erdal.nayir:legacy_codes/konum2.py
        self.vehicle = arac
        # Socket Create
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host_name = socket.gethostname()
        self.socket_address = ("127.0.0.1", 9999)

        # Socket Bind
        self.server_socket.bind(self.socket_address)

        # Socket Listen
        self.server_socket.listen(2)

        Thread(target=self.telem_connect).start()

    def telem_connect(self):
        i = 0
        kamikaze_ip = "111.111.1.111"
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

                cv2.imshow('TRANSMITTING VIDEO', frame)
                if cv2.waitKey(1) == '13':
                    self.gcs.close()

    def gcs_veri(self):
        while True:
            message = self.vfr_hud()
            self.gcs.sendall(message)
            time.sleep(.5)
            if 1 == 2:
                self.gcs.close()

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
                print("yükseklik=", ms.z)

    def next_mission(self):
        while True:
            ms = self.vehicle.recv_match(type="MISSION_CURRENT", blocking=True)
            if ms is not None:
                print(ms.seq)

    def flightmode(self):
        while True:
            print(self.vehicle.flightmode)
            time.sleep(1)

    def arm(self):
        self.arm_ = self.vehicle.motors_armed()
        print(True if self.arm_ else False)

    def location(self, relative):
        return self.vehicle.location(relative)

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

    def set_param(self, param_name, param_value):
        try:
            self.vehicle.param_set_send(param_name.upper(), param_value)
        except RuntimeError:
            return "Parametre hatalı"
        else:
            return self.get_param(param_name)

<<<<<<< HEAD:konum2.py
class görüntü(veriler):
    def __init__(self,vehicle):
        self.vehicle=vehicle
        self.cap = cv2.VideoCapture(0)#"rtsp://192.168.144.25:8554/main.264"
=======

class Görüntü(Veriler):
    def __init__(self, vehicle):
        super().__init__(vehicle)
        self.loc = None
        self.vehicle = vehicle
        self.x, self.y = 1, 1
        self.cap = cv2.VideoCapture(0)  # "rtsp://192.168.144.25:8554/main.264"
>>>>>>> erdal.nayir:legacy_codes/konum2.py
        desired_fps = 30
        self.cap.set(cv2.CAP_PROP_FPS, desired_fps)
        # Codec ayarı (Örneğin, H.264)
        desired_codec = cv2.VideoWriter_fourcc(*'H264')
        self.cap.set(cv2.CAP_PROP_FOURCC, desired_codec)
<<<<<<< HEAD:konum2.py
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)#3
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)#4
        self.width,self.height=self.cap.get(cv2.CAP_PROP_FRAME_WIDTH),self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        cv2.namedWindow('tam ekran',cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('tam ekran',cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        ret,image = self.cap.read()
        self.oran = (self.height/image.shape[0])
        self.görev = 0 # hedefin bulunup bulunmama biti
   
    def ters_haversine(self,lat_u,lon_u,yön):
=======
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # 3
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # 4
        self.width, self.height = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        cv2.namedWindow('tam ekran', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('tam ekran', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        ret, image = self.cap.read()
        self.oran = (self.height / image.shape[0])

    def ters_haversine(self, lon_u, yön):
>>>>>>> erdal.nayir:legacy_codes/konum2.py
        """ ARAÇTAN ALINACAK VERİLER"""
        self.loc = self.location(True)
        print(self.loc)
        heading = self.loc.heading
        lat1 = self.loc.lat  # yan
        lon1 = self.loc.lng  # dikey
        R = 6371.0
        c = lon_u / (R * 1000)
        a = math.tan(c / 2) ** 2 / (1 + math.tan(c / 2) ** 2)
        dlon = math.asin(2 * math.sqrt(a / (math.cos(math.radians(lat1)) ** 2)))
        dlat = math.asin(math.sqrt(a)) * 2
        # lon2 = math.radians(lon1)-dlon
        # lat2 = math.radians(lat1)+dlat

        if 0 < heading < 90:
            lon2 = math.radians(lon1) - dlon
            lat2 = math.radians(lat1) + dlat
        elif 90 < heading < 180:
            lon2 = math.radians(lon1) + dlon
            lat2 = math.radians(lat1) + dlat
        elif 180 < heading < 270:
            lon2 = math.radians(lon1) + dlon
            lat2 = math.radians(lat1) - dlat
        elif 270 < heading:
            lon2 = math.radians(lon1) - dlon
            lat2 = math.radians(lat1) - dlat
        elif heading == 0:
            if yön > 0:
                lon2 = math.radians(lon1) - dlon
                lat2 = math.radians(lat1) + dlat
            else:
                lon2 = math.radians(lon1) - dlon
                lat2 = math.radians(lat1) - dlat
        elif heading == 90:
            if yön > 0:
                lon2 = math.radians(lon1) + dlon
                lat2 = math.radians(lat1) + dlat
            else:
                lon2 = math.radians(lon1) - dlon
                lat2 = math.radians(lat1) + dlat
        elif heading == 180:
            if yön > 0:
                lon2 = math.radians(lon1) + dlon
                lat2 = math.radians(lat1) - dlat
            else:
                lon2 = math.radians(lon1) + dlon
                lat2 = math.radians(lat1) + dlat
        elif heading == 270:
            if yön > 0:
                lon2 = math.radians(lon1) + dlon
                lat2 = math.radians(lat1) - dlat
            else:
                lon2 = math.radians(lon1) - dlon
                lat2 = math.radians(lat1) - dlat
        """if 0 < heading <90 or 180 < heading < 270:
            lat = dlat*math.cos(h) -1*yön*dlon*math.sin(h)
            lon = dlat*math.sin(h) +1*yön*dlon*math.cos(h)
        else:
            lat = dlat*math.sin(h) +1*yön*dlon*math.cos(h)
            lon = dlat*math.cos(h) -1*yön*dlon*math.sin(h)"""
<<<<<<< HEAD:konum2.py
            
        return math.degrees(lat2),math.degrees(lon2)
    
    def hesapla(self,yukseklik,alan3,orta_nokta):
		self.görev = 1
=======

        return math.degrees(lat2), math.degrees(lon2)

    def hesapla(self, yukseklik, alan3, orta_nokta):
>>>>>>> erdal.nayir:legacy_codes/konum2.py
        """kamera fov açı değeleri"""
        dikey_aci_ileri = 25
        dikey_aci_geri = 25
        yatay_aci_sol = 70
        yatay_aci_sağ = 10

        yatay_pixsel = int((1920 * math.tan(math.radians(yatay_aci_sağ))) / (
                math.tan(math.radians(yatay_aci_sol)) + math.tan(math.radians(yatay_aci_sağ))))
        dikey_pixsel = int((1080 * math.tan(math.radians(dikey_aci_geri))) / (
                math.tan(math.radians(dikey_aci_ileri)) + math.tan(math.radians(dikey_aci_geri))))

        tan_y = (1080 - dikey_pixsel - alan3[1]) * math.tan(math.radians(dikey_aci_ileri)) / (1080 - dikey_pixsel)
        tan_x = (1920 - yatay_pixsel - alan3[0]) * math.tan(math.radians(yatay_aci_sol)) / (1920 - yatay_pixsel)
        gercek_uzaklik_yatay = tan_x * (math.sqrt(pow((yukseklik * math.tan(math.radians(dikey_aci_ileri)) * (
                1080 - dikey_pixsel - alan3[1]) / (1080 - dikey_pixsel)), 2) + pow(yukseklik, 2)))
        gercek_uzaklik_dikey = tan_y * (math.sqrt(pow((yukseklik * math.tan(math.radians(yatay_aci_sol)) * (
                1920 - yatay_pixsel - alan3[0]) / (1920 - yatay_pixsel)), 2) + pow(yukseklik, 2)))
        if gercek_uzaklik_dikey == 0 and gercek_uzaklik_yatay == 0:
            pass

        elif gercek_uzaklik_dikey == 0:
            if alan3[1] < yatay_pixsel:
                aci = dikey_aci_ileri
            else:
                aci = dikey_aci_geri
            print((math.tan(math.radians(aci)) * pow(pow(yukseklik, 2) + pow(gercek_uzaklik_yatay, 2), 1 / 2)))

        elif gercek_uzaklik_yatay == 0:
            if alan3[1] < dikey_pixsel:
                pass
            else:
                pass

        else:
            pass

        sağ = 1
        sol = -1
        if orta_nokta[0] >= alan3[0]:
            yön = sağ
        else:
            yön = sol
        return (gercek_uzaklik_yatay, gercek_uzaklik_dikey), (
            self.ters_haversine(gercek_uzaklik_dikey, yön))

    def camera(self):
        yatay_pixsel2, dikey_pixsel2 = self.width, self.height

        """ aranacak kırmızı renk kodları"""
        red_lower = np.array([167, 145, 201])
        red_upper = np.array([179, 238, 255])

        while True:
            ret, image = self.cap.read()
            nokta_x, nokta_y = int(yatay_pixsel2 / self.oran), int(dikey_pixsel2 / self.oran)

            renk = (255, 0, 0)
            renk2 = (0, 0, 255)
            image = cv2.line(image, (int(yatay_pixsel2 / self.oran), 0),
                             (int(yatay_pixsel2 / self.oran), int(self.height / self.oran)), renk, 2)
            image = cv2.line(image, (0, int(dikey_pixsel2 / self.oran)),
                             (int(self.width / self.oran), int(dikey_pixsel2 / self.oran)), renk, 2)
            hsvFrame = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            red_mask = cv2.inRange(hsvFrame, red_lower, red_upper)
            contours, hierarchy = cv2.findContours(red_mask, 1, 2)
            objectCounterRed = 1

            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 300:
                    if objectCounterRed == 1:
                        x, y, w, h = cv2.boundingRect(contour)
                        image = cv2.rectangle(image, (x, y),
                                              (x + w, y + h),
                                              (0, 0, 255), 2)
                        a = int(x + w / 2)
                        b = int(y + h / 2)
                        cv2.circle(image, (a, b), 2, (255, 0, 0), -1)

                        gercek_uzaklik, gercek_konum = self.hesapla(self.loc.alt, (a * self.oran, b * self.oran),
                                                                    (yatay_pixsel2,
                                                                     dikey_pixsel2))  # kısım kalmak zorunda
                        image = cv2.line(image, (nokta_x, nokta_y), (nokta_x, int(b)), renk2, 2)
                        image = cv2.line(image, (nokta_x, nokta_y), (int(a), nokta_y), renk2, 2)
                        cv2.putText(image, str(gercek_uzaklik[1]) + "metre", (nokta_x, int((b + nokta_y) / 2)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
                        cv2.putText(image, str(gercek_uzaklik[0]) + "metre", (int((a + nokta_x) / 2), nokta_y + 25),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)

                        cv2.putText(image, (str(gercek_konum[0]) + " " + str(gercek_konum[1])), (int(a), int(b - 15)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)

                    objectCounterRed += 1
            cv2.imshow("tam ekran", image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.cap.release()
                cv2.destroyAllWindows()
                break
            
class Gorev():
	def __init__(self):
		self.drone = Drone()
		self.veriler = veriler(self.drone.vehicle)
		self.görüntü=görüntü(self.drone.vehicle)
		
		Thread(self.görüntü.camera())
		
	def baslat(self):
		self.drone.vehicle_mode = "GUIDED"
		drone.arm_drone = True
		drone.takeoff(15)
		drone.vehicle_mode = "AUTO"
		
		self.kontrol()
	
	def kontrol(self):
		while True:
			if self.görev == 1 and self.veriler.next_mission == 1:#toplam wp sayısı olacak:
				self.drone.reposition()#araçtan gelen konum verisi yazılacak
				
			elif self.veriler.next_mission == # wp konumların bitip bitmediği ve bulunup bulunmamanın tüm olasılıları yazılacak
			
		

drone = Drone()

<<<<<<< HEAD:konum2.py
veri = veriler(drone.vehicle)

görüntü= görüntü(drone.vehicle)
=======
#veri = Veriler(drone.vehicle)
görüntü= Görüntü(drone.vehicle)
"""

>>>>>>> erdal.nayir:legacy_codes/konum2.py
görüntü.ters_haversine(1,1,2)
"""
#veri.sys_status()

drone.vehicle_mode = "GUIDED"
print(drone.vehicle_mode)
drone.arm_drone = True
print(drone.arm_drone)
drone.takeoff(15)
time.sleep(15)

#drone.goto()

drone.move(ileri=5,yan=1,dikey=0)
time.sleep(2)
"""
<<<<<<< HEAD:konum2.py
#drone.change_alt(-10)
#drone.recv()
#time.sleep(10)
#drone.change_speed()
#drone.multi_copter_to_fixed_wing("drone")
#drone.upload_mission("yollar.txt")
#drone.vehicle_mode = "AUTO"
=======
drone.change_alt(-10)
# drone.recv()
# time.sleep(10)
# drone.change_speed()
# drone.multi_copter_to_fixed_wing("drone")
# drone.upload_mission("yollar.txt")
# drone.vehicle_mode = "AUTO"
>>>>>>> erdal.nayir:legacy_codes/konum2.py
