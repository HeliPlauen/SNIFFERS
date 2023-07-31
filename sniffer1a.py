# pip install scapy
# pip install cryptography
# pip install PyX

import scapy.all as scapy
from scapy.layers import http
from scapy.layers.inet import IP, UDP


# Global variables
LOOP_VALUE = 60
UNKNOWN_VALUE = 31


# Create the sniffing function
def sniff(interface):

    # Get the all packeges information were sniffed and call the exercuted function    
    capture = scapy.sniff(iface=interface, timeout=LOOP_VALUE, prn=sniffed_packet)  
    
    # Get sniffing result
    print("Summary:")
    capture.summary()    

    # Write down data into file
    scapy.wrpcap("T.txt", capture)
    scapy.wrpcap("T.cap", capture)
    print("WE HAVE ALREADY WRITTEN DATA INTO THE FILE")

    # Get traffic size
    total_traffic = 0
    counter = 0
    for pkt in capture:
        if pkt.haslayer(IP):

            # Add IP length
            print(f"Length from IP: {pkt[IP].len}")
            total_traffic += pkt[IP].len

            if pkt.haslayer(UDP):
                print(f"Length from UDP: {pkt[UDP].len}")  

            # Add some undefined length
            total_traffic += UNKNOWN_VALUE                
            print(f"Total traffic is: {total_traffic}")
        else:
            print("Something another!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        counter += 1
        print(f"Counter: {counter}")

# The function executing each package
def sniffed_packet(packet):

    # If HTTP request
    if packet.haslayer(http.HTTPRequest):

        # Get a hierarchical view of an assembled version of the packet
        print(f"HTTP Packet in details: {packet.show()}")

        # Host name
        print(f"HTTP Host: {packet[http.HTTPRequest].Host}")

    print(f"Packet: {packet}")


# Main function
def main():
    print("Sniffer started")

    # Call the sniffing function
    sniff(None)

    #Read adat out off the file
    print("DATA WE HAVE GOTTEN OUT OFF THE FILE: ")
    pkts = scapy.sniff(offline="T.txt")
    for pkt in pkts:
        if pkt.haslayer(http.HTTPRequest):
            print(pkt.show())
    print("FINISH!!!!!")

    
# Start program
if __name__ == "__main__":
    main()