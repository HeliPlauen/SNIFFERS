import socket
import time


# Create client socket
sock = socket.socket()
print("Client created")

# Connect client to server
sock.connect(('localhost', 443))
print("Client was bound to host")

# Send data to server
file_name = input("Input file name please: ")
file_name += '\0'
sock.send(file_name.encode())
print("The data was sent to server")
time.sleep(2)
sock.close()
