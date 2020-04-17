import socket
import threading, time
from datetime import datetime
from protocol import Packet, Protocol
import argparse

protocol = Protocol()

def processConn(address, data):
    start = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    pkt = Packet()
    try:
        try:
            f = open(data,'r')
            print(data)
            data = f.read()
            print(data)
            f.close()

        except:
            print("No such file found.")
            data = "NSF"
            pkt.makePacket(data)
            toSendPack = str(pkt.seq) + protocol.delim + str(pkt.checksum) + protocol.delim + str(pkt.msglen) + protocol.delim + str(pkt.message)
            toSendPack = toSendPack.encode()
            sock.sendto(toSendPack, address)
            return
        
        #send data to client in packets of size MTU
        data_sent = 0
        leng = len(data)
        packets = 0
        retransmissions = 0
        protocol.resetMTU()

        while data_sent < (leng/protocol.mtu):
            packets += 1
            msg = data[data_sent * protocol.mtu : protocol.mtu * (data_sent + 1)]
            pkt.makePacket(msg)
            toSendPack = str(pkt.seq) + protocol.delim + str(pkt.checksum) + protocol.delim + str(pkt.msglen) + protocol.delim + str(pkt.message)
            print(toSendPack)
            #ack = protocol.sendData(sock, toSendPack, address)
            sock.sendto(toSendPack.encode(), address)
            sock.settimeout(4)
            try:
                ack, address = sock.recvfrom(100)
                ack = ack.decode()
            except Exception as e:
                print(e)
                print("Timeout. Resending...")
                retransmissions += 1
                continue
            '''    
            if ack == -1:
                print("Timed out. Retransmitting...")
                retransmissions += 1
                continue
            '''
            if ack.split(",")[0] == str(pkt.seq):
                pkt.seq = int(not pkt.seq)
                print(address," ACKed at ", str(datetime.now()))
                data_sent += 1
        sock.close()
        print(packets, " packets transmitted.")
        print(retransmissions, " retransmissions.")
        print("Time Elapsed: ", str(time.time()-start))
    except Exception as e:
        print(e)
        print("Server Error")

if __name__=="__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    parser = argparse.ArgumentParser(description='Send and receive files on Reliable UDP')
    parser.add_argument('-ip', help='Server IP')
    parser.add_argument('-p', metavar='PORT', type=int, default = 1060, help = 'UDP port')
    args = parser.parse_args()
    server.bind((args.ip, args.p))

    while True:
        data, addr = server.recvfrom(600)
        data = data.decode()
        thread = threading.Thread(target=processConn, args=(addr, data))
        thread.start()
