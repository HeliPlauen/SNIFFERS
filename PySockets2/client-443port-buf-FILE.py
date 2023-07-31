import socket
import time


# Global variable
BUFFER_DIMENTION = 1024


# Create client socket
sock = socket.socket()
print("Client created")

# Connect client to server
sock.connect(('localhost', 443))
print("Client was bound to host")

# Send data to server
file_name = input("Input file name please: ")

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
            sock.send(chunk)            

except FileNotFoundError:

    # If file not found - send message
    sock.send(b'File not found')
    print(f'File "{file_name}" not found')

print("The data was sent to server")
time.sleep(2)
sock.close()
