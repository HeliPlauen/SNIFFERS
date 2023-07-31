
import socket
import sys
import struct
import re


# Get packet and return its header 
def receiveData(s):
    data = ""
    try:
        data = s.recvfrom(65565)
    except timeout:
        data = ""
    except Exception as e:
        print(f"An error happened: {e}")
        sys.exec_info()
    return data[0]


# Get the time of service
def getTOS(data):
    precedence = {0: "Routine", 1: "Priority", 2: "Immediate", 3: "Flash", 4: "Flash override", 5: "CRITIC?ECP", 6: "Internetwork control", 7: "Network control"}
    delay = {0: "Normal delay", 1: "Low delay"}
    throughput = {0: "Normal throughput", 1: "High throughput"}
    reability = {0: "Normal reability", 1: "High reability"}
    cost = {0: "Normal monetary cost", 1: "Minimize monetary cost"}

    D = data & 0x16    # 00010011  & 00010000 = 00010000
    D >>= 4            # 00010010 -> 00000001
    T = data & 0x8     # 00001011  & 00001000 = 00001000
    T >>= 3            # 00001010 -> 00000001
    R = data & 0x4     # 00000111  & 00000100 = 00000100
    R >>= 2            # 00000100 -> 00000100
    M = data & 0x2     # 00000111  & 00000010 = 00000010
    M >>= 2            # 00000010 -> 00000100

    tabs = '\n\t\t\t'  # New line \ Tab \ Tab \ Tab
    TOS = precedence[data >> 5] + tabs + delay[D] + tabs + throughput[T] + tabs + reability[R] + tabs + cost[M]
    return TOS


# Get flags
def getFlags(data):
    flagR = {0: '0 - Reserved bit'}
    flagDF = {0: '0 - Fragment if necessary', 1: '1 - Do not fragmnt'}
    flagMF = {0: '0 - LastFragment', 1: 'More fragments'}

    R = data & 0x8000      # 10011000 00000011  & 10000000 00000000 = 10000000 00000000
    R >>= 15               # 10000000 00000000 -> 00000000 00000001
    DF = data & 0x4000     # 11011000 00000011  & 01000000 00000000 = 01000000 00000000
    DF >>= 14              # 01000000 00000000 -> 00000000 00000001
    MF = data & 0x2000     # 10111000 00000011  & 00100000 00000000 = 00100000 00000000
    MF >>= 13              # 00100000 00000000 -> 00000000 00000001

    tabs = '\n\t\t\t'  # New line \ Tab \ Tab \ Tab
    flags = flagR[R] + tabs + flagDF[DF] + tabs + flagMF[MF]
    return flags


# Get protocol
def getProtocol(protocolNr):
    protocolFile = open('Protocol.txt', 'r')
    protocolData = protocolFile.read()
    protocol = re.findall(r'\n' + str(protocolNr) + ' (?:.)+\n', protocolData)
    if protocol:
        protocol = protocol[0]
        protocol = protocol.replace('\n', '')
        protocol = protocol.replace(str(protocolNr), '')
        protocol = protocol.lstrip()
        return protocol
    else:
        return "No such protocol was found"


# The main function
def main():

    # The public network interface
    HOST = socket.gethostbyname(socket.gethostname())

    # Create the raw socket and bind it to the public interface
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
    s.bind((HOST, 0))

    # Include IP headers
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    # Receive all packets
    s.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    # Start to work forever
    counter = 0
    while True:

        # Receive a apckage
        data = receiveData(s)

        # Divide it into 2 chars, 3 shorts, 2 chars, 1 short and 2 strings for 4 chars each
        unpackedData = struct.unpack("!BBHHHBBH4s4s", data[:20])

        # Divide 1-st element - char into Vetrsion and Internet Header Length (IHL)
        version_IHL = unpackedData[0]
        version = version_IHL >> 4                  # Shift it into 4 bits to the right
        IHL = version_IHL & 0xF                     # 01001010 & 00001111 = 00001010

        # Get Different services (2-nd - char)
        TOS = unpackedData[1]

        # Get total length (3-rd - short)
        totalLength = unpackedData[2]

        # Get Identification (4-th - short)
        ID = unpackedData[3]

        # Divide the 5-th - short into Flags & Fragments offset
        flags = unpackedData[4]
        fragmentOffset = unpackedData[4] & 0x1FFF    # 10111000 00000011 & 00011111 11111111 = 00011000 00000011

        # Get TTL (time to live) (6-th - char)
        TTL = unpackedData[5]

        # Get Protocol (7-th - char)
        protocolNr = unpackedData[6]

        # Get Header Checksum (8-th - short)
        checksum = unpackedData[7]

        # Get source address (9-th string) and destination address (10-th - strong)
        sourceAddress = socket.inet_ntoa(unpackedData[8])
        destinationAddress = socket.inet_ntoa(unpackedData[9])

        # Output data
        print("THE IP PACKET:")
        print(f"Raw data: {data}")
        print(f"Parsed data: {unpackedData}")
        print("\nParced data:")
        print(f"Version:\t\t {version}")
        print(f"Header Length:\t\t {IHL*4} bytes")
        print(f"Type of Service:\t {getTOS(TOS)}")
        print(f"Length:\t\t\t {totalLength}")
        print(f"ID:\t\t\t {hex(ID)} ({ID})")
        print(f"Flags:\t\t\t {getFlags(flags)}")
        print(f"Fragment offcet:\t {fragmentOffset}")
        print(f"Time to Live:\t\t {TTL}")
        print(f"Protocol:\t\t {getProtocol(protocolNr)}")
        print(f"Checksum:\t\t {checksum}")
        print(f"Source:\t\t\t {sourceAddress}")
        print(f"Destination:\t\t {destinationAddress}")
        print(f":Payload:\n {data[20:]}")

        # Increase counter and check if we have to exit
        counter += 1
        if counter == 3:
            break

    # Disable promiscuous mode
    s.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)


# Start executing
if __name__ == "__main__":
    main()