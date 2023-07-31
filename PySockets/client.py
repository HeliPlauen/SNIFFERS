import socket


# Create client socket
sock = socket.socket()
print("Client created")

# Connect client to server
sock.connect(('localhost', 9090))
print("Client was bound to host")

# Send data to server
sock.send('hello, world!!!'.encode())
print("The data was sent to server")

# Receive data of 1024 B
data = sock.recv(1024)
sock.close()

print(f"We receiver from server: {data.decode()}")