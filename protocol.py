import socket
import time
import hashlib
from datetime import datetime



class Packet():
    message = 0
    seq = 0
    msglen = 0
    checksum = 0

    def makePacket(self, info):
        self.checksum = hashlib.sha1(info.encode()).hexdigest()
        self.message = info
        self.msglen = len(str(info))


class Protocol():
    delim = "|::|"
    __mtu = 50
    timeout = 5
    seqFlag = 0
    message = 0
    seq = 0
    msglen = 0
    checksum = 0

    def makePacket(self, info):
        self.checksum = hashlib.sha1(info.encode()).hexdigest()
        self.message = info
        self.msglen = len(str(info))
    
    def __init__(self):
        print("---Reliable UDP protocol initiated---")

    def changeMTU(self, newMTU):
        self.__mtu = newMTU
        if(newMTU > 65535):
            self.__mtu = 65535
    
    def resetMTU(self):
        self.__mtu = 50

    def getMTU(self):
        return self.__mtu

    def resetTimeout(self):
        self.timeout = 1


    def sendPacket(self, sock, data, address):
        self.makePacket(data)
        data = str(self.seq) + self.delim + str(self.checksum) + self.delim + str(self.msglen) + self.delim + str(self.message)
        data = data.encode()
        send = sock.sendto(data, address)
        print("Packet with ", send, " bytes of data sent to client at ",address)
        sock.settimeout(self.timeout)
        try:
            ack, address = sock.recvfrom(self.__mtu)
            ack = ack.decode()
            return ack
        except:
            return str(-1)