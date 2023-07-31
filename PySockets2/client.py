import socket
import time


# Global variables
HTTP_PORTING = 9090
BUFFER_DIMENTION = 1024

# Create client socket
sock = socket.socket()
print("Client created")

# Connect client to server
sock.connect(('localhost', HTTP_PORTING))
print("Client was bound to host")

# Send data to server
file_name = input("Input file name please: ")
sock.send(file_name.encode())
print("The data was sent to server")

# Receive data of 1024B
summary_data = b""
bytes_counter = 0
while True:
    data = sock.recv(BUFFER_DIMENTION)
    summary_data += data
    bytes_counter += len(data)
    print(bytes_counter)
    if len(data) < BUFFER_DIMENTION:
        break

print(f"THE SUMMARY DATA IS: {summary_data}")
sock.close()

#print(f"We receiver from server: {data.decode()}")
print(f"Number of bytes is: {bytes_counter}")
time.sleep(3)