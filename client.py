import socket
import hashlib
import argparse
from protocol import Protocol
import os

protocol = Protocol()

if __name__=="__main__":
    print("File transfer over reliable UDP")
    parser = argparse.ArgumentParser(description='Send and receive files on Reliable UDP')
    parser.add_argument('-ip', help='Server IP')
    parser.add_argument('-p', metavar='PORT', type=int, default = 1060, help = 'UDP port')
    args = parser.parse_args()
    server_addr = (args.ip, args.p)

    filename = input("File Requested: ")
    newfile =  filename.split(".")[0] + "_client_copy." + filename.split(".")[1]
    f = open(newfile, 'w')

    sock = protocol.createSocket()
    sock.settimeout(10)

    try:
        sock.sendto(filename.encode(), server_addr)
        protocol.seqFlag = 0

        while True:
            #get packet
            seq, msglen, msg, ackstatus = protocol.recvPacket(sock)
            print(msg)
            if not ackstatus:
                continue
            if msg == "NSF":
                print("No such file found at server.")
                os.remove(newfile)
                break
            else:
                f.write(msg)
                print("Seq no: ", seq, " received")
            if int(msglen) < protocol.getMTU():
                seq = 1-int(seq)
                break
    except socket.error as e:
        print(e)
    finally:
        print("Done")
        sock.close()
        f.close()

    