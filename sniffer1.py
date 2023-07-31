import scapy.all as scapy
from scapy.layers import http


# Create the sniffing function
def sniff(interface):

    # Get the all packeges information were sniffed and call the exercuted function    
    capture = scapy.sniff(iface=interface, prn=sniffed_packet)    
    capture.summary()


# The function executing each package
def sniffed_packet(packet):
    #print(f"Packet (summary): {packet.summary()}")

    # If HTTP request
    if packet.haslayer(http.HTTPRequest):

        # Get a hierarchical view of an assembled version of the packet
        print("HTTP request!!!!")

    print(f"Packet in details: {packet.show()}")


# Main function
def main():
    print("Sniffer started")

    # Call the sniffing function
    #sniff("MyWiFiName")
    sniff(None)
    

if __name__ == "__main__":
    main()