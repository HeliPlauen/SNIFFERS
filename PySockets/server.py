import socket


# Create server socket
sock = socket.socket()
print("Server created")

# Bind the socket to host address and port
sock.bind(('', 9090))
print("Server was bound to host")

# Set the number of connections to listen
sock.listen(1)

# Get new socket object and client address
conn, addr = sock.accept()
print(f"Connected: {addr}")
print(f"The socket object is: {conn}")

# Receive data from client
while True:

    # Receive data of 1024 MB at one time
    data = conn.recv(1024)
    if not data:
        break
    
    print(f"We receiver from client: {data.decode()}")
    
    # Send turned to uppercase data back to client
    conn.send(data.upper())

# Close socket
conn.close()