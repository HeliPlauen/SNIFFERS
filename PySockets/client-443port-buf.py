import socket


# Create client socket
sock = socket.socket()
print("Client created")

# Connect client to server
sock.connect(('localhost', 443))
print("Client was bound to host")

# Send data to server and close client socket
message_text = input("Input message to send please: ")
sock.send(message_text.encode())
print("The data was sent to server")
sock.close()

print(f"We receiver from server: {data.decode()}")