import scapy.all as scapy
from scapy.layers import http


def sniff(interface):
    scapy.sniff(iface=interface, store=False, prn=sniffed_packet)


def sniffed_packet(packet):
    if packet.haslayer(http.HTTPRequest):
        #print(packet.show()) 
        print(f"HTTP request: {packet.show()}") 


# IPconfig is the same as ifconfig on UNIX
def main():
    ###sniff(None)
    sniff("enp0s3")


if __name__ == "__main__":
    main()