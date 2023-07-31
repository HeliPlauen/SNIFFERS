
import socket
import os 
import struct
from ctypes import *


#host = "localhost"
host = socket.gethostbyname(socket.gethostname())
buff_size = 65565

class IP(Structure):
    
    _fields_ = [
        ("ihl", c_ubyte, 4),
        ("version", c_ubyte, 4),
        ("tos", c_ubyte),
        ("len", c_ushort),
        ("id", c_ushort),
        ("offset", c_ushort),
        ("ttl", c_ubyte),
        ("protocol_num", c_ubyte),
        ("sum", c_ushort),
        ("src", c_uint),
        ("dst", c_uint),
    ]
    
    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)
    
    def __init__(self, socket_buffer=None):
        self.protocol_map = {1 : "ICMP", 6 : "TCP", 17 : "UDP"}
        self.src_address = socket.inet_ntoa(struct.pack("<L", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)
        
if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP 
    
sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
sniffer.bind((host, 0))
print("[*] Starting...")

sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

try:
    counter = 0
    while True:
        raw_buffer = sniffer.recvfrom(buff_size)[0]
        ip_header = IP(raw_buffer[0:20])
        print(raw_buffer)
        print(ip_header)
        print(f"Protocol Version: {ip_header.version}")
        print(f"Length: {ip_header.ttl}")
        print(f"Protocol: {ip_header.protocol} {ip_header.src_address} -> {ip_header.dst_address}") 
        counter += 1
        if counter == 10:
            break
except KeyboardInterrupt:
    print("\n[*] Closing.")            
    if os.name == "nt":        
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
except Exception as err:
    print(f"\n[*] {err}")    
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF) 
        
# Disable promiscuous mode
sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
    