
import socket


# The public network interface
HOST = socket.gethostbyname(socket.gethostname())

# Create the raw socket and bind it to the public interface
s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
s.bind((HOST, 0))

# Include IP headers
s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# Receive all packets
s.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

# Receive a apckage
print(s.recvfrom(65565))

# Disable promiscuous mode
s.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
