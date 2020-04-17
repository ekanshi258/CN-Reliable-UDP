import socket
import time
import hashlib
from datetime import datetime


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
        if(newMTU > 65430):
            self.__mtu = 65430
    
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

    def sendPackets(self, sock, data, address):
        data_sent = 0
        leng = len(data)
        packets = 0
        retrans = 0
        
        while(data_sent < (leng/self.__mtu)):
            packets+=1
            msg = data[data_sent * self.__mtu : self.__mtu * (data_sent + 1)]
            ack = self.sendPacket(sock, msg, address)
            if ack == str(-1):
                retrans += 1
                print("Timed out. Retransmitting (", retrans,")...")
                continue
            
            if ack.split(",")[0] == str(self.seq):
                self.seq = int(not self.seq)
                print(address," ACKed at ", str(datetime.now()))
                data_sent += 1
        return packets, retrans

    def sendACK(self, sock, length, address):
        sock.sendto((str(self.seqFlag) + "," + str(length)).encode(), address)
        self.seqFlag = 1-self.seqFlag

    def readPacket(self, sock, data, address):
        data = data.decode()
        seq = data.split(self.delim)[0]
        server_checksum = data.split(self.delim)[1]
        msglen = data.split(self.delim)[2]
        msg = data.split(self.delim)[3]
        ack = True
        client_checksum = hashlib.sha1(msg.encode()).hexdigest()
        if server_checksum == client_checksum and self.seqFlag == int(seq):
            self.sendACK(sock, msglen, address)
        elif server_checksum == client_checksum and self.seqFlag != int(seq):
            print("Duplicate, discarded")
            ack = False
        else:
            print("Checksum does not match. Data Corrupted. Dropping and waiting for retransmission")
            ack = False
        return seq, msglen, msg, ack