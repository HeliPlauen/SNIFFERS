
#include <winsock2.h>
#include <Ws2tcpip.h>
#include <iostream>
#include <stdlib.h>
#include <string>

#include <windows.h>

// Link with ws2_32.lib
#pragma comment(lib, "Ws2_32.lib")

/*
* RAW socket
* Server socket
* Sniffer
* TCP - DOES NOT WORK!!!!!!!!!!! WE CAN'T RECEIVE TCP PACKETS IN RAW!!!!!!!
*/


// Global variables
int BUF_LENGTH = 4096;

// SIO_RCVALL !!!!!
#define SIO_RCVALL  _WSAIOW(IOC_VENDOR,1)


// IP Header structure
typedef struct ip_hdr {
    unsigned char ip_verlen;
    unsigned char ip_tos;
    unsigned short ip_total_len;
    unsigned short ip_id;
    unsigned short ip_offset;
    unsigned char ip_ttl;
    unsigned char ip_protocol;
    unsigned short ip_checksum;
    unsigned int sourceIP;
    unsigned int destIP;
} IP_HDR;


// TCP Header structure
typedef struct tcp_hdr {
    // TODO
} TCP_HDR;


void ShowError(char* msg);
USHORT checksum(USHORT* buffer, int size);
int __cdecl main() {

    // Create variables  !!!!!!!!!!!!!!!!!!!!!!!!!!      
    IP_HDR ipHdr;
    TCP_HDR udpHdr;
    char buf[BUF_LENGTH];

    // Initialize socket
    WSADATA wsaData;                             // The containing socket data strucure
    if (WSAStartup(MAKEWORD(2, 2), &wsaData)) {
        ShowError("The socket was not initialized!");
        return 1;
    }
    std::cout << "WSAStartup - OK" << std::endl;

    // Create socket
    SOCKET sckt;
    sckt = socket(AF_INET, SOCK_RAW, IPPROTO_TCP);
    if (sckt == INVALID_SOCKET) {
        ShowError("The socket was not created!");
        WSACleanup();
        return 2;
    }
    std::cout << "Raw scoket is created" << std::endl;

    // Get our local host name
    CHAR szHostName[16];
    if (gethostname(szHostName, sizeof szHostName)) {
        ShowError("The hos name was not gotten!");
        WSACleanup();
        closesocket(sckt);
        return 3;
    }
    std::cout << "Host name: " << szHostName << std::endl;

    // Get our local host address
    HOSTENT* phe = gethostbyname(szHostName);   
    int err = WSAGetLastError();
    if (err) {
        ShowError("The host address was not gotten!");
        WSACleanup();
        closesocket(sckt);
        return 4;
    }
    std::cout << "Host address: " << phe << std::endl;
    std::cout << "Host address: " << inet_ntoa(*((struct in_addr*)phe->h_addr_list[0])) << std::endl;

    SOCKADDR_IN sa;
    ZeroMemory(&sa, sizeof sa);
    sa.sin_family = AF_INET;
    sa.sin_addr.s_addr = ((struct in_addr*)phe->h_addr_list[0])->s_addr;
    std::cout << "Host address in SOCKADDR_IN: " << sa.sin_addr.s_addr << std::endl;

    // Bind socket
    if (bind(sckt, (SOCKADDR*)&sa, sizeof(sa)) == SOCKET_ERROR) {        
        ShowError("The address was not bound to the socket!");
        printf("Bind error: %i\n", WSAGetLastError());
        WSACleanup();
        closesocket(sckt);
        return 5;
    }
    std::cout << "Bind - OK." << std::endl;

    // Turn on promiscuous regime receive all the packets)
    DWORD flag = TRUE;
    if (ioctlsocket(sckt, SIO_RCVALL, &flag) == SOCKET_ERROR) {
        ShowError("The promiscuous regime is off!");
        WSACleanup();
        closesocket(sckt);
        return 6;
    }
    std::cout << "Promiscuous regime - OK." << std::endl;

    // Set socket options
    BOOL opt = TRUE;
    if (setsockopt(sckt, SOL_SOCKET, SO_EXCLUSIVEADDRUSE, (char*)&opt, sizeof(opt)) == SOCKET_ERROR) {
        ShowError("The socket options were not set!");
        WSACleanup();
        closesocket(sckt);
        return 7;
    }
    std::cout << "Setsockopt - OK" << std::endl;

    // Receive packets
    int counter = 0;
    while (true) {        
        int request;
        request = recv(sckt, buf, BUF_LENGTH, 0);
        if (request == SOCKET_ERROR) {
            ShowError("The socket listening was not started!");
            WSACleanup();
            closesocket(sckt);
            return 8;
        }

        // Get IP header
        IP_HDR* ipHeader = (IP_HDR*)buf;         

        // Get source IP        
        IN_ADDR iaddr;
        iaddr.s_addr = ipHeader->sourceIP;
        std::cout << "Source: " << ipHeader->sourceIP << std::endl;
        std::cout << "Source: " << inet_ntoa(iaddr) << std::endl;

        // Get destination IP
        iaddr.s_addr = ipHeader->destIP;
        std::cout << "Destaddr: " << ipHeader->destIP << std::endl;
        std::cout << "Source: " << inet_ntoa(iaddr) << std::endl;

        // Get protocol
        std::cout << "Protocol: " << int(ipHeader->ip_protocol) << std::endl;
        std::cout << "----------------------------------------\n";

        // Get TCP header
        TCP_HDR* tcpHeader = (TCP_HDR*)buf;

        // Try to exit the loop
        counter++;
        if (counter == 10) {
            break;
        }
    }

    // Close socket
    if (closesocket(sckt) == SOCKET_ERROR) {
        ShowError("The socket was not closed!");
        return 55;
    }

    // Close and cleanup socket
    if (WSACleanup())
    {
        ShowError("The Winsock DLL library usage was not stopped!");
        return 66;
    }
    std::cout << "WSACleanup - OK" << std::endl;
    return 0;
}


// Error function
void ShowError(char* msg) {
    std::cout << "Error: " << msg << std::endl;
}


// The UDP checksum counting function
USHORT checksum(USHORT* buffer, int size)
{
    unsigned long cksum = 0;
    while (size > 1) {
        cksum += *buffer++;
        size -= sizeof(USHORT);
    }
    if (size) {
        cksum += *(UCHAR*)buffer;
    }
    cksum = (cksum >> 16) + (cksum & 0xffff);
    cksum += (cksum >> 16);
    return (USHORT)(~cksum);
}

