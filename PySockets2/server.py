import socket


# Global variables
HTTP_PORTING = 9090
HTTP_ADDRESS = ''
BUFFER_DIMENTION = 1024

# Create server socket
sock = socket.socket()

# Bind the socket to host address and port
sock.bind((HTTP_ADDRESS, HTTP_PORTING))

# Set the number of connections to listen
sock.listen(5)
print('Server listening...')

# Get new socket object and client address
loopcounter = 0
while True:
    client, addr = sock.accept()
    print(f"Connected: {addr}")

    # Receive the file name
    file_name = client.recv(BUFFER_DIMENTION).decode()

    try:

        # Open the file for reading in binary
        with open(file_name, 'rb') as file:

            # Read file in chunks
            while True:
                chunk = file.read(BUFFER_DIMENTION)
                if not chunk:
                    break
    
                print(f"We receiver from client: {chunk}")
    
                # Send turned to uppercase data back to client
                client.sendall(chunk)            

    except FileNotFoundError:

        # If file not found - send message
        client.sendall(b'File not found')
        print(f'File "{file_name}" not found')

    loopcounter += 1
    if loopcounter == 10:
        break

# Close socket
client.close()