import scapy.all as scapy
from scapy.layers import http


def sniff(interface):
    scapy.sniff(iface=interface, store=False, prn=sniffed_packet)


def sniffed_packet(packet):
    if packet.haslayer(http.HTTPRequest):
        print(f"HTTP request: {packet.show()}")


def main():
    print("Sniffer started")

    #sniff("enp0s3")
    sniff("MyWiFiName")


if __name__ == "__main__":
    main()