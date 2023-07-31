
import scapy.all as scapy
from scapy.layers.inet import IP
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import ARP, LLC
import sys


class Sniffer:
    def __init__(self, users_loop_value, users_ethernert_value=31, users_total_traffic=0):
        self.loop_value = users_loop_value
        self.ethernert_value = users_ethernert_value
        self.total_traffic = users_total_traffic

    # Sniffing, write data into the file and return traffic value
    def sniff(self, interface):
        print("START SNIFFING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        # Get the all packeges information were sniffed and call the exercuted function 
        capture = scapy.sniff(iface=interface, timeout=self.loop_value)

        # Get traffic size
        for pkt in capture:
            if pkt.haslayer(IP):

                # Add IP length
                additional_traffic = pkt[IP].len
                self.total_traffic += additional_traffic 

                # Add ethernet header length
                self.total_traffic += self.ethernert_value                

            elif pkt.haslayer(IPv6):                

                # Add IPv6 length
                additional_traffic = pkt[IPv6].plen
                self.total_traffic += additional_traffic

                # Add ethernet and IPv6 (24 bytes) headers lengths
                self.total_traffic += (self.ethernert_value + 24)               

            elif pkt.haslayer(ARP):

                # Add ARP header length
                self.total_traffic += 28

            elif pkt.haslayer(LLC):

                # Add 802.3 packet length
                additional_traffic = pkt.len + 29
                self.total_traffic += additional_traffic

            else:
                print("SOMETHING ANOTHER BUT NOT IP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print(pkt.show())
                print(f"Total traffic is: {self.total_traffic}")

        print(f"Total traffic is: {self.total_traffic}")
        print("FINISH SNIFFING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return self.total_traffic


"""   
# Start program
if __name__ == "__main__":
    #S = Sniffer(10, 31, 0)
    S = Sniffer(10)
    print(S.sniff(None))
    print(S.get_data_out_off_the_file())
    S.get_packet_out_of_the_file(10)
    S.get_packet_out_of_the_file(100)
"""