# pip install scapy
# pip install cryptography
# pip install PyX

import scapy.all as scapy
from scapy.layers import http
from scapy.layers.inet import IP, UDP
import sys


# Global variables
LOOP_VALUE = 60
UNKNOWN_VALUE = 31
TOTAL_TRAFFIC = 0


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
    global TOTAL_TRAFFIC
    counter = 0
    for pkt in capture:
        if pkt.haslayer(IP):

            # Add IP length
            additional_traffic = pkt[IP].len
            print(f"Length from IP: {additional_traffic}")
            TOTAL_TRAFFIC += additional_traffic

            if pkt.haslayer(UDP):
                print(f"Length from UDP: {pkt[UDP].len}")  

            # Add some undefined length
            TOTAL_TRAFFIC += UNKNOWN_VALUE                
            print(f"Total traffic is: {TOTAL_TRAFFIC}")
        else:
            print("Something another!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            sys.exit()        
        print(f"Counter: {counter}")
        counter += 1


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
        print(pkt.summary())
        if pkt.haslayer(http.HTTPRequest):
            print(pkt.show())
    print("FINISH!!!!!!!!!!!!!!!!!!!!!!!")
    print(f"TOTAL TRAFFIC: {TOTAL_TRAFFIC}")

    
# Start program
if __name__ == "__main__":
    main()