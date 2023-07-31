#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <stdio.h>
#include <netinet/in.h>
#include <sys/stat.h>
#include <unistd.h>
#include <iostream>

using namespace std;


int main(int argc, char **argv) 
{
    int sockfd, n;
    char *sendline,datagram[4096];
    cout<<datagram<<endl;
    struct sockaddr_in servaddr;
    struct ip *iphead = (struct ip*)datagram;
    struct icmphdr *icphead = (struct icmphdr*)datagram+sizeof(struct ip);
    iphead->ip_hl = 5;
    iphead->ip_v=4;
    iphead->ip_tos=0;
    iphead->ip_len=sizeof(struct ip)+sizeof(struct icmphdr);
    iphead->ip_id=htonl(54321);
    iphead->ip_off=0;
    iphead->ip_ttl=255;
    iphead->ip_p=6;
    iphead->ip_sum=0;
    iphead->ip_src.s_addr=servaddr.sin_addr.s_addr;
    iphead->ip_dst.s_addr=servaddr.sin_addr.s_addr;
    icphead->type=0;
    icphead->code=0;
    icphead->checksum=0;
    iphead->ip_sum=iphead->ip_len;

    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(17000);
    servaddr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    sockfd=socket(PF_INET, SOCK_RAW,IPPROTO_ICMP);

    {
        int one=1;
        const int* val=&one;
        if (setsockopt(sockfd,IPPROTO_IP,IP_HDRINCL,val,sizeof(one))<0)
        printf("sockopt");
    }

    cout<<datagram<<endl;
    write(1,"Enter string\n", 13);
    sendline = (char*)datagram+sizeof(struct ip)+sizeof(struct icmphdr);
    n=read(0, sendline, 100);

    int m=sendto(sockfd, sendline, n+sizeof(struct ip)+sizeof(struct icmphdr), 0, (struct sockaddr *)&servaddr, sizeof(struct sockaddr_in));
    printf("отправлено %d\n",m);
    cout<<datagram<<endl;
    close(sockfd);
    return 0;
}