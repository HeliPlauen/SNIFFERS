#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <stdio.h>
#include <netinet/in.h>
#include <sys/stat.h>
#include <unistd.h>
#include <arpa/inet.h>

#include <stdlib.h>
#include <string.h>


int main() {
    int sockfd, n;

    //char mesg[65536];
    unsigned char *mesg = (unsigned char *)malloc(65536);

    struct sockaddr_in ADR;

    sockfd = socket(PF_INET, SOCK_RAW, IPPROTO_TCP);
    if (sockfd == -1) {
        printf("Socket error\n");
        return 1;
    }

    printf("bind\n");
    printf("starts...\n");
    recvfrom(sockfd, mesg, 65536, 0 ,NULL, NULL);
    printf("REQUEST: %s \n", (char*)(mesg));
    printf("length: %li \n", strlen((char*)(mesg)));
    return 0;
}