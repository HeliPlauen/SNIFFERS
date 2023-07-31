
import scapy.all as scapy
from scapy.layers import http
from scapy.layers.inet import IP
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import ARP
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
        #capture = scapy.sniff(iface=interface, timeout=self.loop_value, prn=lambda packet:print(packet))
        capture = scapy.sniff(iface=interface, timeout=self.loop_value)

        # Write down data into file
        scapy.wrpcap("T.cap", capture)
        print("WE HAVE ALREADY WRITTEN DATA INTO THE FILE")

        # Get traffic size
        counter = 0
        for pkt in capture:
            if pkt.haslayer(IP):

                # Add IP length
                additional_traffic = pkt[IP].len
                #print(f"Length from IP: {additional_traffic}")
                self.total_traffic += additional_traffic 

                # Add ethernet header length
                self.total_traffic += self.ethernert_value                
                #print(f"Total traffic is: {self.total_traffic}")
            elif pkt.haslayer(IPv6):                

                # Add IPv6 length
                additional_traffic = pkt[IPv6].plen
                #print(f"Length from IP: {additional_traffic}")
                self.total_traffic += additional_traffic

                # Add ethernet and IPv6 (24 bytes) headers lengths
                self.total_traffic += (self.ethernert_value + 24)               
                #print(f"Total traffic is: {self.total_traffic}")
            elif pkt.haslayer(ARP):

                # Add ARP header length
                self.total_traffic += 28               
                #print(f"Total traffic is: {self.total_traffic}")
            else:
                print("SOMETHING ANOTHER BUT NOT IP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print(pkt.show())
                print(f"Total traffic is: {self.total_traffic}")
                #sys.exit()
            counter += 1
        print(f"Total traffic is: {self.total_traffic}")
        print("FINISH SNIFFING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return self.total_traffic

    # Read data out of the file and return traffic value
    def get_data_out_off_the_file(self, filename="T.cap"):
        print("START GETTING DATA OUT OFF THE FILE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        pkts = scapy.sniff(offline=filename)
        for pkt in pkts:
            #print(pkt.summary())
            if pkt.haslayer(http.HTTPRequest) or pkt.haslayer(IPv6) or pkt.haslayer(ARP):
                print(pkt.show())
        print(f"TOTAL TRAFFIC: {self.total_traffic}")
        print("GETTING DATA OUT OFF THE FILE IS FINISHED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")        
        return self.total_traffic

    # Read chosrn packet ot of the file and print its details
    def get_packet_out_of_the_file(self, packet_number, filename="T.cap"):
        print("START GETTING PACKAGE OUT OFF THE FILE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        pkts = scapy.sniff(offline=filename)
        if packet_number > len(pkts) - 1:
            print("No packet with such number!!!!!")
        for i in range(len(pkts)):
            if i == packet_number:
                print(pkts[i].show())
        print("GETTING PACKAGE OUT OFF THE FILE IS FINISHED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")  


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