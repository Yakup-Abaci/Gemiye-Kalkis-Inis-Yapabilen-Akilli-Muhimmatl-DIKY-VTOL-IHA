import time
from pymavlink import mavutil, mavwp
#from pymavlink.dialects.v10 import ardupilotmega as mavlink1

class Drone:
    def __init__(self):
        mavutil.set_dialect("ardupilotmega")
        self.vehicle = mavutil.mavlink_connection('tcp:127.0.0.1:5762', baud=115200)
        #self.vehicle_mode = None
        #self.arm_drone = None
        #self.param = None
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
        
    @property
    def vehicle_mode(self):
        while True:
            msg = self.vehicle.recv_match(type="HEARTBEAT")
            if msg is not None and msg.type != 6:
                break
        return self.vehicle.flightmode
        """
        self.__vehicle_mode = mavutil.mode_string_apm(msg.custom_mode)
        return self.__vehicle_mode"""
    
    @vehicle_mode.setter
    def vehicle_mode(self,mode):
        if mode.upper() in mavutil.mode_mapping_apm.values():
            for key,value in mavutil.mode_mapping_apm.items():
                if value == mode.upper():
                    self.vehicle.flightmode = self.vehicle.set_mode_apm(key)
        else:
            self.vehicle.flightmode = self.vehicle.flightmode
    
    @property
    def arm_drone(self):
        self.__arm_drone = self.vehicle.motors_armed()
        return True if self.__arm_drone else False
    
    @arm_drone.setter
    def arm_drone(self,arm):
        if arm:
            self.vehicle.arducopter_arm()
            self.vehicle.motors_armed_wait()
            self.__arm_drone = True
        else:
            self.vehicle.arducopter_disarm()
            self.vehicle.motors_disarmed_wait()
            self.__arm_drone = False
    
    def yaw(self,heading):
        self.vehicle.mav.set_attitude_target(
            self.vehicle.target_system,  # target_system
            self.vehicle.target_component,
            mavutil.mavlink.ATTITUDE_TARGET_TYPEMASK_BODY_YAW_RATE_IGNORE,  # command
            0,  # confirmation
            mavutil.mavlink.HEADING_TYPE_HEADING,  # param1 (1 to indicate arm)
            heading,  # param2 (all other params meaningless)
            1000,  # param3
            0,  # param4
            0,  # param5
            0,  # param6
            0)  # param7
        msg = self.vehicle.recv_match(type=['COMMAND_ACK'], blocking=True)
        print(msg)
            
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
            if self.vehicle.recv_match(type="GLOBAL_POSITION_INT",blocking=True).relative_alt*0.001 > altitude*0.95:
                print("yüksekliğe ulaşıldı")
                break
            else:
                print("yükseklik",self.vehicle.recv_match(type="GLOBAL_POSITION_INT",blocking=True).relative_alt*0.001)

    def land(self,altitude):
        self.vehicle.mav.command_long_send(
            self.vehicle.target_system,  # target_system
            self.vehicle.target_component,
            mavutil.mavlink.MAV_CMD_NAV_LAND,  # command
            0,  # confirmation
            0,  # param1 (1 to indicate arm)
            0,  # param2 (all other params meaningless)
            0,  # param3
            0,  # param4
            0,  # param5
            0,  # param6
            altitude)  # param7
        while True:
            if self.vehicle.recv_match(type="GLOBAL_POSITION_INT",blocking=True).relative_alt*0.001 < 1*0.95:
                print("iniş yapıldı")
                break
            else:
                print("yükseklik",self.vehicle.recv_match(type="GLOBAL_POSITION_INT",blocking=True).relative_alt*0.001)

        
    def vtol_takeoff(self, altitude):
        self.vehicle.mav.command_long_send(
            self.vehicle.target_system,  # target_system
            self.vehicle.target_system,
            mavutil.mavlink.MAV_CMD_NAV_VTOL_TAKEOFF,  # command
            0,  # confirmation
            0,  # param1 (1 to indicate arm)
            0,  # param2 (all other params meaningless)
            0,  # param3
            0,  # param4
            0,  # param5
            0,  # param6
            altitude)  # param7
        while True:
            location = self.vehicle.location(True)
            if float(str(location).split(",")[2].split('=')[1]) > altitude*0.95:
                print("yüksekliğe ulaşıldı")
                break
            else:
                print("yükseklik",float(str(location).split(",")[2].split('=')[1]))
                
    def change_alt(self,altitude):
        if altitude > 0:
            çarpan = 1
        else:
            çarpan = -1
        location = self.vehicle.recv_match(type="POSITION_TARGET_GLOBAL_INT",blocking=True).alt
        self.vehicle.mav.set_position_target_global_int_send(
            time_boot_ms=0,
            target_system=self.vehicle.target_system,
            target_component=self.vehicle.target_component,
            coordinate_frame=mavutil.mavlink.MAV_FRAME_GLOBAL_INT,
            type_mask=0b00000111000111,
            lat_int=0,
            lon_int=0,
            alt=location+altitude,
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
        hedef = self.vehicle.recv_match(type="POSITION_TARGET_GLOBAL_INT",blocking=True).alt - location
        while True:
            yukseklik = self.vehicle.recv_match(type="GLOBAL_POSITION_INT",blocking=True).relative_alt / 1000.0
            print(hedef)
            if yukseklik*çarpan > hedef*0.95*çarpan:
                print("hedefe ulaşıldı")
                break
            else :
                print("yükseklik ",yukseklik)

    def move(self):
        location = self.vehicle.recv_match(type="POSITION_TARGET_GLOBAL_INT",blocking=True)
        self.vehicle.mav.set_position_target_global_int_send(
            time_boot_ms=0,
            target_system=self.vehicle.target_system,
            target_component=self.vehicle.target_component,
            coordinate_frame=mavutil.mavlink.MAV_FRAME_GLOBAL_INT,
            type_mask=0b00000000111000,
            lat_int=location.lat_int,
            lon_int=location.lon_int,
            alt=location.alt+10,
            vx=0,
            vy=0,
            vz=0,
            afx=0,
            afy=0,
            afz=0,
            yaw=0,
            yaw_rate=0
        )
        """while True:
            msg = self.vehicle.recv_match(type=["POSITION_TARGET_GLOBAL_INT","LOCAL_POSITION_NED"])
            if msg is not None:
                print(msg)"""
        print('sent')
    
    def move2(self,vx,vy):
        #location = self.vehicle.recv_match(type="POSITION_TARGET_LOCAL_NED",blocking=True)
        self.vehicle.mav.set_position_target_local_ned_send(
            time_boot_ms=0,
            target_system=self.vehicle.target_system,
            target_component=self.vehicle.target_component,
            coordinate_frame=mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            type_mask=0b110111000111,#0b00001111000111,0b110111000111 
            x=0,
            y=0,
            z=0,
            vx=vx,
            vy=vy,
            vz=0,
            afx=0,
            afy=0,
            afz=0,
            yaw=0,
            yaw_rate=0)

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

    def add_mission(self,komut,lat,long,alt):
        mission_cmds = {"takeoff":mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            "waypoint":mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            "rtl":mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
            "land":mavutil.mavlink.MAV_CMD_NAV_LAND,
            "loiter":mavutil.mavlink.MAV_CMD_NAV_LOITER_UNLIM}
        command = mission_cmds[komut] if komut in  mission_cmds else 0
        p = mavutil.mavlink.MAVLink_mission_item_message(self.vehicle.target_system,
                                                                     self.vehicle.target_component,
                                                                     0, mavutil.mavlink.MAV_FRAME_GLOBAL_TERRAIN_ALT,
                                                                     command,
                                                                     0, 0, 0, 0,0, 0,
                                                                     lat, long, alt)
        if not self.gorev:
            self.waypoint_loader.add(p)
            self.gorev = True
            
        self.waypoint_loader.add(p)
        self.vehicle.waypoint_count_send(self.waypoint_loader.count())
       
        for i in range(self.waypoint_loader.count()):
            self.vehicle.mav.send(self.waypoint_loader.wp(msg.seq))
            print('Sending waypoint {0}'.format(msg.seq))
        
    def get_params(self):
        self.vehicle.param_fetch_all()
        #while True:
            #msg = self.vehicle.recv_match(type='PARAM_VALUE', blocking=True)
            #if msg is not None:
                #print(f"param_id = {msg.param_id} param_value = {msg.param_value}")
                
       
    def get_param(self,param_name):
        try:
            self.vehicle.param_fetch_one(param_name.upper())
        except Exception:
            return "Parametre hatalı"
        else:
            msg = self.vehicle.recv_match(type='PARAM_VALUE', blocking=True)
            return f"param_id = {msg.param_id} param_value = {msg.param_value}"
            

    def set_param(self,param_name,param_value):
        try:
            self.vehicle.param_set_send(param_name.upper(),value)
        except Exception:
            return  "Parametre hatalı"
        else:
            return  self.get_param(param_name)
            
    def location(self):
        return self.vehicle.location()
            
    def close_connection(self):
        self.vehicle.close()
        
    def yazdir(self):
        while True:
            print(self.vehicle.flightmode)
            time.sleep(1)
        #print(self.vehicle.mav_type)
        #print(self.vehicle.base_mode)
        #self.vehicle.recv_match(type='VFR_HUD', blocking=True)
        #self.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        #print(self.vehicle.messages['GLOBAL_POSITION_INT'])
        #print(self.vehicle.messages['VFR_HUD'])
        #print(self.vehicle.messages['HEARTBEAT'])
        #self.get_params()
        #time.sleep(2)
        #print(self.vehicle.params)
    
    def set_servo(self): # atanmayan serco pinleri için çalışıyor
        #self.vehicle.set_servo(10,1_200)
        """self.vehicle.mav.command_long_send(self.vehicle.target_system, self.vehicle.target_component,
                                   mavutil.mavlink.MAV_CMD_DO_REPEAT_SERVO, 0,
                                   9, 0,
                                   5, 1, 0, 0, 0)"""
        self.vehicle.mav.rc_channels_override()
     
    def recv(self):
        #capability_msg = self.vehicle.mav.command_long_encode(0, 0, mavutil.mavlink.MAV_CMD_REQUEST_AUTOPILOT_CAPABILITIES, 0, 1, 0, 0, 0, 0, 0, 0)
        #self.vehicle.mav.send(capability_msg)
        while True:
            msg = self.vehicle.recv_match(type="AUTOPILOT_VERSION")
            if msg is not None:
                capabilities = msg.capabilities
                break
        mission_float                  = (((capabilities >> 0)  & 1) == 1)
        param_float                    = (((capabilities >> 1)  & 1) == 1)
        mission_int                    = (((capabilities >> 2)  & 1) == 1)
        command_int                    = (((capabilities >> 3)  & 1) == 1)
        param_union                    = (((capabilities >> 4)  & 1) == 1)
        ftp                            = (((capabilities >> 5)  & 1) == 1)
        set_attitude_target            = (((capabilities >> 6)  & 1) == 1)
        set_attitude_target_local_ned  = (((capabilities >> 7)  & 1) == 1)
        set_altitude_target_global_int = (((capabilities >> 8)  & 1) == 1)
        terrain                        = (((capabilities >> 9)  & 1) == 1)
        set_actuator_target            = (((capabilities >> 10) & 1) == 1)
        flight_termination             = (((capabilities >> 11) & 1) == 1)
        compass_calibration            = (((capabilities >> 12) & 1) == 1)
        print("mission_float=",mission_float,"\n param_float=",param_float,"\n mission_int=",mission_int,"\n command_int=",command_int,
                "\n param_union=",param_union,"\n ftp=",ftp,"\n set_attitude_target=",set_attitude_target,
                "\n set_attitude_target_local_ned=",set_attitude_target_local_ned,"\n set_altitude_target_global_int=",set_altitude_target_global_int,
                "\n terrain=",terrain,"\n set_actuator_target=",set_actuator_target,"\n flight_termination=",flight_termination,
                "\n compass_calibration=",compass_calibration)
        
    def channels(self):
            while True:
                msg = self.vehicle.recv_match(type="RC_CHANNELS")
                if msg is not None:
                    print(msg)

drone = Drone()
#drone.send_heartbeat()
drone.vehicle_mode = "GUIDED"
#print(drone.vehicle_mode)
drone.arm_drone = True
#print(drone.arm_drone)
drone.takeoff(2)
#drone.change_alt(25)
time.sleep(10)
#print("move verildi")
#drone.yaw(100)
drone.move2(2,0)
time.sleep(2)
drone.move2(0,2)
time.sleep(2)
drone.move2(0,0)
time.sleep(2)
drone.land(0)
drone.arm_drone = False
drone.close_connection()
#time.sleep(10)
#drone.move2(0)
#drone.yazdir()
#drone.recv()
#drone.set_servo()
#drone.channels()
