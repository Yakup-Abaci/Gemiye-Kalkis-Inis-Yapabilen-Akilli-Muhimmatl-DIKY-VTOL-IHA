import time

from pymavlink import mavutil, mavwp


class KamikazeDrone:
    def __init__(self):
        self.vehicle = mavutil.mavlink_connection('tcp:127.0.0.1:5762', baud=961)

        self.waypoint_loader = mavwp.MAVWPLoader(self.vehicle.target_system, self.vehicle.target_component)
        self.vehicle.wait_heartbeat()

        self.gorev = False

    def send_heartbeat(self):
        self.vehicle.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_FIXED_WING,
                                        mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA,
                                        8,
                                        0,
                                        0,
                                        0)
        while True:
            msg = self.vehicle.recv_match(type='HEARTBEAT')
            if msg is not None:
                print("HEARTBEAT:", msg)

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

    def arm_drone(self,arm):#arm 0= disarm, arm=1 arm
        self.vehicle.mav.command_long_send(
            self.vehicle.target_system,  # target_system
            self.vehicle.target_system,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,  # command
            0,  # confirmation
            arm,  # param1 (1 to indicate arm)
            0,  # param2 (all other params meaningless)
            0,  # param3
            0,  # param4
            0,  # param5
            0,  # param6
            0)  # param7
        self.vehicle.motors_armed()

    def takeoff(self,altitude):

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

    def set_auto(self):
        self.vehicle.mav.command_long_send(self.vehicle.target_system,
                                           self.vehicle.target_component,
                                           mavutil.mavlink.MAV_CMD_DO_SET_MODE,
                                           0, 1, 10, 0, 0, 0, 0, 0)


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
            if yukseklik * çarpan > hedef * 0.95 * çarpan:
                break 

    def cmd_set_home(self, home_location, altitude):
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
            self.vehicle.mav.send(self.waypoint_loader.wp(i.seq))
            print('Sending waypoint {0}'.format(i.seq))

    def location(self):
        return self.vehicle.location()

    def close_connection(self):
        self.vehicle.close()

    def kamikaze_infos(self):
        print(self.vehicle.flightmode)
        # print(self.vehicle.mav_type)
        # print(self.vehicle.base_mode)
        # self.vehicle.recv_match(type='VFR_HUD', blocking=True)
        # self.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        # print(self.vehicle.messages['GLOBAL_POSITION_INT'])
        # print(self.vehicle.messages['VFR_HUD'])
        # print(self.vehicle.messages['HEARTBEAT'])
        # self.get_params()
        # time.sleep(2)
        # print(self.vehicle.params)

    def set_rc(self):  # 3 sn
        self.vehicle.mav.rc_channels_override_send(self.vehicle.target_system, self.vehicle.target_component,
                                                   1500, 1500, 0, 1500, 0, 0, 0, 0) # rudder eleron elevator kanalları için
    
