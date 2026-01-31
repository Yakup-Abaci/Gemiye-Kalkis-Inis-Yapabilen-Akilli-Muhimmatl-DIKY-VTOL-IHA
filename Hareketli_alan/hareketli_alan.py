import pymavlink
import time

class hareketli_alan:
    def __init__(self,com):
        self.hareketli_alan = mavutil.mavlink_connection(com, baud=115200)
        
    def location(self):
        loc = self.hareketli_alan.location(True)
        loc = loc.split(",")
        for i,l in enumerate(loc):
            l.split("=")
            konum[i]=l[1]
        return konum

    def hız(self):
        msg = self.heliport.recv_match(type="VFR_HUD", blocking=True)
        if msg is not None:
            return msg.groundspeed
  
    