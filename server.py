import socket
import threading, time
from datetime import datetime
from protocol import Protocol
import argparse

protocol = Protocol()

def processConn(address, data):
    start = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        try:
            f = open(data,'r')
            print(data)
            data = f.read()
            f.close()

        except:
            print("No such file found.")
            data = "NSF"
            ack = protocol.sendPacket(sock,data, address)
            print("Client informed. Removing Client.")
            sock.close()
            return
        
        #send data to client in packets of size MTU
        packets, retransmissions = protocol.sendPackets(sock, data, address)
        '''
        data_sent = 0
        leng = len(data)
        packets = 0
        retransmissions = 0
        protocol.resetMTU()

        while data_sent < (leng/protocol.getMTU()):
            packets += 1
            toSendPack = data[data_sent * protocol.getMTU() : protocol.getMTU() * (data_sent + 1)]
            ack = protocol.sendPacket(sock, toSendPack, address)
            
            if ack == str(-1):
                print("Timed out. Retransmitting...")
                retransmissions += 1
                continue
            
            if ack.split(",")[0] == str(protocol.seq):
                protocol.seq = int(not protocol.seq)
                print(address," ACKed at ", str(datetime.now()))
                data_sent += 1
        '''
        sock.close()
        print("\nTransfer done.")
        print(packets, " packets transmitted.")
        print(retransmissions, " retransmissions.")
        print("Time Elapsed: ", str(time.time()-start))
    except Exception as e:
        print(e)
        print("Server Error")

if __name__=="__main__":
    print("File transfer over Reliable UDP")
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    parser = argparse.ArgumentParser(description='Send and receive files on Reliable UDP')
    parser.add_argument('-ip', help='Server IP')
    parser.add_argument('-p', metavar='PORT', type=int, default = 1060, help = 'UDP port')
    args = parser.parse_args()
    server.bind((args.ip, args.p))

    while True:
        data, addr = server.recvfrom(1024)
        data = data.decode()
        print("\n\nClient at ", addr)
        thread = threading.Thread(target=processConn, args=(addr, data))
        thread.start()
