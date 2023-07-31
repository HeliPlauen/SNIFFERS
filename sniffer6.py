
import socket
import struct
import textwrap


# Mine global variables
addr = 'localhost'
porting = 0
buff_size = 65565


# Main function
def main():
    print("MAIN!!!!!!")
    # conn = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(3))  # For Linux only!!
    conn = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)    # For Windows 

    # Mine!!!!!!!!!!!!
    global addr, porting
    conn.bind((addr, porting))
    conn.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    conn.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    print("RAW Socket is ready")

    while True:
        raw_data, addr = conn.recvfrom(buff_size)
        dset_mac, src_mac, eth_proto, data = ethernet_frame(raw_data)
        print("\nEtherner Frame:")
        print("Destination: {}, Source: {}, Protocol: {}".format(dset_mac, src_mac, eth_proto))
        print("------------------------------------------------------------------------------------------------\n")



# Unpack Enternet frame
def ethernet_frame(data):
    print("Unpack Enternet frame!!!!!!")
    dest_mac, src_mac, proto = struct.unpack('! 6s 6s H', data[:14])                        # Get first 14 bytes
    print(f"We have gotten form struct: {struct.unpack('! 6s 6s H', data[:14])}")
    print(f"dest_mac: {dest_mac}, src_mac: {src_mac}, proto: {src_mac}")
    return get_mac_addr(dest_mac), get_mac_addr(src_mac), socket.htons(proto), data[14:]    # Return addresses, type(HTTP) and data[14:last]


# Return properly formatted NAC address (AA:BB:CC:DD:EE:FF)
def get_mac_addr(bytes_addr):
    print("Return properly formatted NAC address!!!!!!")
    bytes_str = map('{:02x}'.format, bytes_addr)
    print(f"bytes_str: {bytes_str}")
    mac_addr = ":".join(bytes_str).upper()
    print(f"mac_addr: {mac_addr}")
    return mac_addr


# Start function
if __name__ == "__main__":
    main()