import socket
import time
import hashlib
from datetime import datetime



class Packet():
    message = 0
    seq = 0
    msglen = 0
    checksum = 0
    retransmit = False

    def makePacket(self, info):
        self.checksum = hashlib.sha1(info.encode()).hexdigest()
        self.message = info
        self.msglen = len(str(info))


class Protocol():
    delim = "|::|"
    mtu = 500
    timeout = 1
    seqFlag = 0
    
    def __init__(self):
        print("---Reliable UDP protocol initiated---")

    def changeMTU(self, newMTU):
        self.mtu = newMTU
        if(newMTU > 65535):
            self.mtu = 65535
    
    def resetMTU(self):
        self.mtu = 500

    def changeTimeout(self, seconds):
        self.timeout = seconds

    def resetTimeout(self):
        self.timeout = 1


    def sendData(self, sock, data, address):
        data = data.encode()
        send = sock.sendto(data, address)
        print("Packet with ", send, " bytes of data sent to client at ",address,". Waiting for acknowledgement...")
        sock.settimeout(self.timeout)
        try:
            ack, address = sock.recvfrom(self.mtu)
            return ack
        except:
            return -1