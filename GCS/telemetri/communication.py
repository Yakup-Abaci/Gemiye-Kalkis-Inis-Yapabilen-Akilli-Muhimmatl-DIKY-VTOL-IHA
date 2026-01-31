import socket, cv2, pickle, struct
from threading import Thread

class haberleşme:
    def __init__(self):
        self.host_ip = '192.168.0.142'  # paste your server ip address here
        self.veri = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        port = 9996
        socket_address = (self.host_ip,port)
        self.veri.connect(socket_address)
        Thread(target=self.goruntu)
        Thread(target=self.ana_arac)
        Thread(target=self.ana_arac_gonder)
        
    def goruntu(self): # ana araçtan çekilecek görüntü
        # create socket
        client= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = 9999
        client.connect((self.host_ip, port))  # a tuple
        data = b""
        payload_size = struct.calcsize("Q")
        while True:
            while len(data) < payload_size:
                packet = client.recv(4 * 1024)  # 4K
                if not packet: break
                data += packet
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(data) < msg_size:
                data += client.recv(4 * 1024)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            frame = pickle.loads(frame_data)
            return frame
        
    def ana_arac(self):
        # Socket Create
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        port = 9998
        socket_address = (self.host_ip,port)
        client.connect(socket_address)
        while True:
            self.data = client.recv(1024)  # receive response
            data = pickle.loads(data)
            self.groundspeed = data["groundspeed"]
            self.airspeed = data["airspeed"]
            self.heading = data["heading"]
            self.next_wp = data["next_wp"]
            self.flightmode = data["flightmode"]
            self.loc = data["loc"]
            
    
    def kamikaze(self):
        # create socket
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = 9999
        client.connect((self.host_ip, port))  # a tuple
        data = b""
        payload_size = struct.calcsize("Q")
        while True:
            while len(data) < payload_size:
                packet = client.recv(4 * 1024)  # 4K
                if not packet: break
                data += packet
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(data) < msg_size:
                data += client.recv(4 * 1024)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            frame = pickle.loads(frame_data)
            return frame
    
    def gonder(self,komut,*args):
        if komut == "baglan":
            message = {"baglan":args[0]}
            data = pickle.dumps(message)
            self.veri.send(data)
            return 0
        elif komut == "arm":
            message = {"arm":args[0]}
            data = pickle.dumps(message)
            self.veri.send(data)
            return 0
        elif komut == "takeoff":
            message = {"takeoff":args[0]}
            data = pickle.dumps(message)
            self.veri.send(data)
            return 0
        elif komut == "mode":
            message = {"mode":args[0]}
            data = pickle.dumps(message)
            self.veri.send(data)
            return 0





