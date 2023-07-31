
import socket
import struct
import binascii


addr = 'localhost'
porting = 0
#porting = 443
#porting = 56421
#buff_size = 2048
buff_size = 65565

sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.htons(0x0800))  # For Linux
#sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
print("RAW Socket is ready")

while True:
    print('Inside the loop')
    packet = sock.recvfrom(buff_size)
    ethernet_header = packet[0][0:14]                                    # Get Ethernet Header 
    eth_header = struct.unpack("!6s6s2s", ethernet_header) 
    print("Destination MAC:" + binascii.hexlify(eth_header[0]).decode() + " Source MAC:" 
          + binascii.hexlify(eth_header[1]).decode() + " Type:" + binascii.hexlify(eth_header[2]).decode())