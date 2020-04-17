import socket
import hashlib
import argparse
from protocol import Protocol

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
        protocol.seqFlag = 0

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
            seq, msglen, msg, ackstatus = protocol.readPacket(sock, data, server_addr)
            if not ackstatus:
                continue
            if msg == "NSF":
                print("No such file found at server.")
                f.write("This file was not transferred correctly")
                break
            else:
                f.write(msg)
                print("Seq no: ", seq, " received")
            if int(msglen) < protocol.getMTU():
                seq = 1-int(seq)
                break
    finally:
        print("Done")
        sock.close()
        f.close()

    