import socket


# Create server socket
sock = socket.socket()
print("Server created")

# Bind the socket to host address and port
sock.bind(('', 9090))
print("Server was bound to host")

# Set the number of connections to listen
sock.listen(5)

# Get new socket object and client address
loopcounter = 0
while True:
    data_summary = 0
    conn, addr = sock.accept()
    print(f"Connected: {addr}")
    print(f"The socket object is: {conn}")

    # Receive data from client
    while True:

        # Receive data of 15B at one time
        data = conn.recv(15)
        if not data: 
            break
    
        print(f"Summary we receiver from client: {data.decode()} bytes")
        data_summary += int(data.decode())

    loopcounter += 1
    if loopcounter == 10:
        break

# Close socket
conn.close()