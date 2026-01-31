import time
from pymavlink import mavutil, mavwp
#import busio
#import board
#from adafruit_pca9685 import PCA9685
#from adafruit_servokit import ServoKit


class Drone:
    def __init__(self, servo_count=16, pwm_frequency=50):
        self.__arm_drone = None
        self.vehicle = mavutil.mavlink_connection('tcp:127.0.0.1:5762', baud=115200)
        self.heliport = mavutil.mavlink_connection('tcp:127.0.0.1:5762', baud=115200) # rfd ile bağlantı
        mavutil.set_dialect("ardupilotmega")

        self.waypoint_loader = mavwp.MAVWPLoader(self.vehicle.target_system, self.vehicle.target_component)
        self.vehicle.wait_heartbeat()
        self.home = False
        self.gorev = False

        # PCA9685 ile servo kontrol değişkenleri
        #self.i2c = busio.I2C(board.SCL, board.SDA)
        #self.pca = PCA9685(self.i2c)
        #self.pca.frequency = pwm_frequency

        # ServoKit kullanarak servo yönetim değişkeni
        #self.kit = ServoKit(channels=servo_count)

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

        if not self.home:
            self.cmd_set_home(home_location, home_altitude)
            self.home = True
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

    def reposition(self,lat,lon,alt):
        #self.vehicle.mav.command_long_send(0, 0, mavutil.mavlink.MAV_CMD_GET_HOME_POSITION, 0, 0, 0, 0, 0, 0, 0, 0)
        #alt = self.vehicle.recv_match(type="HOME_POSITION", blocking=True).altitude / 1e3

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
        
    def set_param(self, param_name, param_value):
        try:
            self.vehicle.param_set_send(param_name.upper(), param_value)
        except RuntimeError:
            return "Parametre hatalı"
        else:
            return self.get_param(param_name)
    
    def kamera_dondur(self):
        self.set_servo_angle_servokit(12,90)

    def set_servo_angle_servokit(self, pin:int, angle):
        """
            Belirtilen servo numarasına belirli bir açı gönderir.
            Servo numaraları 0-15 arasındadır ve açı 0-180 derece arasında olmalıdır.
        """

        # Servo açısını ayarla
        self.kit.servo[pin].angle = angle
        time.sleep(1)
        return True

    def set_servo_pca9865(self, pwm_value):
        """
            Belirtilen servo numarasına belirli bir PWM değeri gönderir.
            Servo numaraları 0-15 arasındadır ve PWM değeri 0-4095 arasındadır.
        """

        # PWM değerini mikro saniyeden (1000-2000) 12-bit çözünürlüğe (0-4095) dönüştür
        pulse_length = int((pwm_value / 20000) * 4096)

        # PCA9685 kanalına duty cycle gönder
        self.pca.channels[17].duty_cycle = pulse_length
        print(f"Servo 17 PWM değeri {pwm_value} olarak ayarlandı")
