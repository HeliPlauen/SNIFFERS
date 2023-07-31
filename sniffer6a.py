
import socket
import struct
import textwrap


# [*] Ethernet [*]
    # [*] IPv4 [*]
        # fsdf
        # dsadfast
            # [*] TCP [*]
                # fastdf
                # dasdasf 

TAB_1 = '\t    '
TAB_2 = '\t\t    '
TAB_3 = '\t\t\t    '
TAB_4 = '\t\t\t\t    '

DATA_TAB_1 = '\t  '
DATA_TAB_2 = '\t\t  '
DATA_TAB_3 = '\t\t\t  '
DATA_TAB_4 = '\t\t\t\t  '


# Mine global variables
buff_size = 65565


# Main function
def main():
    print("MAIN!!!!!!")

    # The public network interface
    HOST = socket.gethostbyname(socket.gethostname())

    # Create the raw socket and bind it to the public interface   
    conn = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)    # For Windows 
    #conn = socket.socket(socket.AF_INET, socket.SOCK_RAW, 0)
    conn.bind((HOST, 0))

    # Include IP headers
    conn.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    # Receive all packets
    conn.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    print("RAW Socket is ready")

    counter = 0
    while True:
        raw_data, addr = conn.recvfrom(buff_size)

        # It seems, that AF_INET does not handle Ethernet
        """
        dset_mac, src_mac, eth_proto, data = ethernet_frame(raw_data) 
        print(f"Raw_Data {raw_data}\n Addr: {addr}")
        
        # Ethenet
        print("\nEtherner Frame:")
        print(TAB_1 + "Destination: {}, Source: {}, Protocol: {}".format(dset_mac, src_mac, eth_proto))  # eth_proto IS USELESS in Windows
        """

        # IT IS VERY BAD BUT I FIND NOTHING BETTER !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Processing POSSIBLE IP
        unpackedDataIP = struct.unpack("!B", raw_data[:1])
        checking_if_protocol_is_IP = unpackedDataIP[0] >> 4
        print(f"{TAB_1} IP protocol from IP {checking_if_protocol_is_IP}")
        # IT IS VERY BAD BUT I FIND NOTHING BETTER !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # If IP (8 for IP)
        #if eth_proto == 8:
            #(version, header_length, ttl, proto, src, target, data) = ipv4_packet(data)
        # IT IS VERY BAD BUT I FIND NOTHING BETTER !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if checking_if_protocol_is_IP == 4:            
            (version, header_length, ttl, proto, src, target, data) = ipv4_packet(raw_data)
            # IT IS VERY BAD BUT I FIND NOTHING BETTER !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            print(TAB_1 + "IPv4 packet: ")
            print(TAB_2 + "Version: {}, Header length: {}, Total length: {}".format(version, header_length, ttl)) 
            print(TAB_2 + "Protocol: {}, Source: {}, Target: {}".format(proto, src, target)) 

            # If ICMP (1 for ICMP)
            if proto == 1:
                icmp_type, code, checksum, data = icmp_packet(data)
                print(TAB_1 + "ICMP packet: ")
                print(TAB_2 + "Type: {}, Code: {}, Checksum: {}".format(icmp_type, code, checksum)) 
                print(TAB_2 + "Data: ")
                print(format_multi_line(DATA_TAB_3, data))

            # If TCP (6 for TCP)
            elif proto == 6:
                (src_port, dest_port, sequence, acknowledgement, flags_urg, flags_ack, flags_psh, flags_rst, flags_syn, flags_fin, data) = tcp_segment(data)
                print(TAB_1 + "TCP segment: ")
                print(TAB_2 + "Source port: {}, Destination port: {}".format(src_port, dest_port)) 
                print(TAB_2 + "Sequence: {}, Acknowledgement: {}".format(sequence, acknowledgement)) 
                print(TAB_2 + "Flags: ")
                print(TAB_3 + "URG: {}, ACK: {}, PSH: {}, RTS: {}, SYN: {}, FIN: {}".format(flags_urg, flags_ack, flags_psh, flags_rst, flags_syn, flags_fin)) 
                print(TAB_2 + "Data: ")
                print(format_multi_line(DATA_TAB_3, data))

            # If UDP (17 for UDP)
            elif proto == 17:
                src_port, dest_port, length, data = udp_segment(data)
                print(TAB_1 + "UDP segment: ")
                print(TAB_2 + "Source port: {}, Destination port: {}, Length: {}".format(src_port, dest_port, length)) 

                print(TAB_2 + "Data: ")
                print(format_multi_line(DATA_TAB_3, data))

            # Other
            else:
                print(TAB_1 + "Data: ")
                print(format_multi_line(DATA_TAB_2, data))
                break

        else: 
            print("Data: ")
            print(format_multi_line(DATA_TAB_1, data))
            break
        
        print("------------------------------------------------------------------------------------------------\n")
        counter += 1
        if counter == 100:
            break

    # Disable promiscuous mode
    conn.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
    print("Promiscuous mode is disabled!!!")


# It seems, that AF_INET does not handle Ethernet
"""
# Unpack Enternet frame
def ethernet_frame(data):
    print("Unpack Enternet frame!!!!!!")
    dest_mac, src_mac, proto = struct.unpack('! 6s 6s H', data[:14])                        # Get first 14 bytes
    print(f"Protocol: {proto} {socket.htons(proto)}")
    print(f"We have gotten form struct: {struct.unpack('! 6s 6s H', data[:14])}")
    print(f"dest_mac: {dest_mac}, src_mac: {src_mac}, proto: {proto}")
    #return get_mac_addr(dest_mac), get_mac_addr(src_mac), socket.htons(proto), data[14:]    # Return addresses, type(HTTP) and data[14:last]
    return get_mac_addr(dest_mac), get_mac_addr(src_mac), socket.htons(proto), data[14:] 


# Return properly formatted MAC address (AA:BB:CC:DD:EE:FF)
def get_mac_addr(bytes_addr):
    print("Return properly formatted NAC address!!!!!!")
    bytes_str = map('{:02x}'.format, bytes_addr)
    print(f"bytes_str: {bytes_str}")
    mac_addr = ":".join(bytes_str).upper()
    print(f"mac_addr: {mac_addr}")
    return mac_addr
"""


# Unpack IPv4 packet
def ipv4_packet(data):
    version_header_length = data[0]                    # We have 8 bits array
    version = version_header_length >> 4               # Shift it into the right in 4 bit (1-st half (right) - version)
    header_length = (version_header_length & 15) * 4   # XXXXXXXX & 00001111 (2-nd half (leht) - header length)
    ttl, proto, src, target = struct.unpack('! 8x B B 2x 4s 4s', data[:20])
    return version, header_length, ttl, proto, ipv4(src), ipv4(target), data[header_length:]


# Returns properly formatted IPv4 address (127.0.0.1)
def ipv4(addr):
    return '.'.join(map(str, addr))


# Unpacks ICMP
def icmp_packet(data):
    icmp_type, code, checksum = struct.unpack('! B B H', data[:4])
    return icmp_type, code, checksum, data[4:]


# Unpack TCP segment
def tcp_segment(data):
    (src_port, dest_port, sequence, acknowledgement, offset_reserved_flags) = struct.unpack('! H H L L H', data[:14])
    offset = (offset_reserved_flags >> 12) * 4
    flags_urg = (offset_reserved_flags & 32) >> 5
    flags_ack = (offset_reserved_flags & 16) >> 4
    flags_psh = (offset_reserved_flags & 8) >> 3
    flags_rst = (offset_reserved_flags & 4) >> 2
    flags_syn = (offset_reserved_flags & 2) >> 1
    flags_fin = offset_reserved_flags & 1
    return src_port, dest_port, sequence, acknowledgement, flags_urg, flags_ack, flags_psh, flags_rst, flags_syn, flags_fin, data[offset:]


# Unpack UDP segment
def udp_segment(data):
    src_port, dest_port, size = struct.unpack('! H H 2x H', data[:8])
    return src_port, dest_port, size, data[8:]


# Format multi-line data
def format_multi_line(prefix, string, size=80):
    size -= len(prefix)
    if isinstance(string, bytes):
        string = ''.join(r'\x{:02x}'.format(byte) for byte in string)
        if size % 2:
            size -= 1
    return '\n'.join([prefix + line for line in textwrap.wrap(string, size)])


# Start function
if __name__ == "__main__":
    main()