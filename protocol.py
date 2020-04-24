import socket
import time
import hashlib
from datetime import datetime

# Protocol class, needs to be instantiated in both server and client programs.
class Protocol():
    delim = "|::|"
    _mtu = 50
    timeout = 1
    seqFlag = 0
    _message = 0
    seq = 0
    msglen = 0
    _checksum = 0
    maxRetrans = 5

    def __init__(self):
        print("---Reliable UDP protocol initiated---")


    # Create a UDP socket
    def createSocket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return sock

    # Assign seq number, checksum, _message length to the packet
    def makePacket(self, info):
        self._checksum = hashlib.sha1(info.encode()).hexdigest()
        self._message = info
        self.msglen = len(str(info))
        data = str(self.seq) + self.delim + str(self._checksum) + self.delim + str(self.msglen) + self.delim + str(self._message)
        return data
    
    # Set a Maximum Transmission Unit size
    def setMTU(self, newMTU):
        self._mtu = newMTU
        if newMTU > 65430:
            self._mtu = 65435
        if newMTU < 32:
            self._mtu = 32
    
    # Reset MTU to default value
    def resetMTU(self):
        self._mtu = 50

    # Get MTU value
    def getMTU(self):
        return self._mtu

    # reset timeout value to default
    def resetTimeout(self):
        self.timeout = 1

    # Function to send a single packet. Recives acknowledgement as well
    def sendPacket(self, sock, data, address):
        data = self.makePacket(data)
        data = data.encode()
        send = sock.sendto(data, address)
        print("Packet with ", send, " bytes of data sent to client at ",address)
        sock.settimeout(self.timeout)
        while True:
            try:
                ack, address = sock.recvfrom(self._mtu)
                ack = ack.decode()

                # check if the ACK is for the correct packet.
                if ack.split(",")[0] != str(self.seq):
                    continue
                return ack
            except:
                return str(-1)

    # Send data in one or more packets. Counts packets and retransmissions.
    def sendPackets(self, sock, data, address):
        data_sent = 0
        leng = len(data)
        packets = 0
        retrans = 0
        cont_retrans = 0
        while(data_sent < (leng/self._mtu) and cont_retrans < self.maxRetrans):
            packets+=1
            msg = data[data_sent * self._mtu : self._mtu * (data_sent + 1)]
            ack = self.sendPacket(sock, msg, address)
            if ack == str(-1):
                retrans += 1
                print("Timed out. Retransmitting (", retrans,")...")
                cont_retrans+=1
                continue
            
            if ack.split(",")[0] == str(self.seq):
                self.seq = int(not self.seq)
                print(address," ACKed at ", str(datetime.now()))
                data_sent += 1
                cont_retrans = 0
        if cont_retrans == self.maxRetrans:
            print("Maximum limit of Continous Retransmissions reached. Closing.")
        return packets, retrans

    # send Acknowledgement
    def sendACK(self, sock, length, address):
        sock.sendto((str(self.seqFlag) + "," + str(length)).encode(), address)
        self.seqFlag = 1-self.seqFlag

    # Decipher and read packet, check for corruptions/duplicates, and send ACK or drop. Return information.
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
            sock.sendto((str(seq) + "," + str(0)).encode(), address)
            ack = False
        else:
            print("_Checksum does not match. Data Corrupted. Dropping and waiting for retransmission")
            ack = False
        return seq, msglen, msg, ack

    # receive a packet and read it
    def recvPacket(self, sock):
        data, address = sock.recvfrom(self._mtu + 100)
        return self.readPacket(sock, data, address)