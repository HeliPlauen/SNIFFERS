
import socket
import struct
import binascii

import re


# Global variables
#host = "localhost"
addr = socket.gethostbyname(socket.gethostname())
porting = 0
buff_size = 65565

# Getting protocol function
def getProtocol(protocolNr):
    protocolFile = open('Protocol.txt', 'r')
    protocolData = protocolFile.read()
    protocol = re.findall(r'\n' + str(protocolNr) + ' (?:.)+\n', protocolData)
    if protocol:
        protocol = protocol[0]
        protocol = protocol.replace('\n', '')
        protocol = protocol.replace(str(protocolNr), '')
        protocol = protocol.lstrip()
        return protocol
    else:
        return "No such protocol was found"

#sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.htons(0x0800))
sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)

sock.bind((addr, porting))
sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
print("RAW Socket is ready")

# It works forever
counter = 0
while True:
    print('Inside the loop')
    packet = sock.recvfrom(buff_size)
    print(packet[0])

    # It seems, that AF_INET does not handle Ethernet
    """
    # Processing ethernet
    ethernet_header = packet[0][0:14]                                # Get Ethernet Header 
    eth_header = struct.unpack("!6s6s2s", ethernet_header) 
    print(eth_header)
    print(
          "Destination MAC:" + binascii.hexlify(eth_header[0]).decode() 
          + " Source MAC:" + binascii.hexlify(eth_header[1]).decode() 
          + " Type:" + binascii.hexlify(eth_header[2]).decode()
    )   
    """ 

    # Processing IP
    unpackedDataIP = struct.unpack("!BBHHHBBH4s4s", packet[0][:20])   # Get IP Header
    print(unpackedDataIP)
    versionIP = unpackedDataIP[0] >> 4
    print(f"Version:\t\t {versionIP}")
    totalLengthIP = unpackedDataIP[2]
    print(f"Length:\t\t\t {totalLengthIP}")
    protocolFromIP = getProtocol(unpackedDataIP[6])
    print(f"Protocol:\t\t {protocolFromIP}")

    # Increase counter and check if we have to exit
    counter += 1
    if counter == 10:
        break

# Disable promiscuous mode
sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)