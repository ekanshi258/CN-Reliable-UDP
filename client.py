import socket
import hashlib
import argparse
from protocol import Packet, Protocol

protocol = Protocol()

if __name__=="__main__":
    print("File transfer over reliable UDP")
    parser = argparse.ArgumentParser(description='Send and receive files on Reliable UDP')
    parser.add_argument('-ip', help='Server IP')
    parser.add_argument('-p', metavar='PORT', type=int, default = 1060, help = 'UDP port')
    args = parser.parse_args()
    server_addr = (args.ip, args.p)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)

    filename = input("File Requested: ")
    f = open( filename.split(".")[0] + "_client_copy." + filename.split(".")[1], 'w')

    try:
        tryConn = 0
        filename = filename.encode()
        sock.sendto(filename, server_addr)
        seqFlag = 0

        while True:
            try:
                data, server_addr = sock.recvfrom(protocol.getMTU() + 100)
                tryConn = 0
            except:
                if tryConn < 4:
                    print("Connection timeout. Retrying...")
                    tryConn += 1
                    continue
                else:
                    print("Maximum connection trials reached")
                    f.write("This file was not transferred correctly")
                    break
            
            #get all info
            data = data.decode()
            seq = data.split(protocol.delim)[0]
            server_checksum = data.split(protocol.delim)[1]
            msglen = data.split(protocol.delim)[2]
            msg = data.split(protocol.delim)[3]
            print(msg)
            client_checksum = hashlib.sha1(msg.encode()).hexdigest()
           # print(msg)
            if server_checksum == client_checksum and seqFlag == int(seq):
                if msg == "NSF":
                    print("No such file found at server.")
                    f.write("This file was not transferred correctly")
                    break
                else:
                    f.write(msg)
                    print("Seq no: ", seq, " received")
                    sock.sendto((str(seq) + "," + str(msglen)).encode(), server_addr)
                    seqFlag = 1-seqFlag
            elif server_checksum == client_checksum and seqFlag != int(seq):
                print("Duplicate, discarded")
                continue
            else:
                print("Checksum does not match. Data Corrupted. Dropping and waiting for retransmission")
                continue
            if int(msglen) < protocol.getMTU():
                seq = 1-int(seq)
                break
    finally:
        print("Done")
        sock.close()
        f.close()

    