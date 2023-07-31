
#include <winsock2.h>
#include <Windows.h>
#include <Ws2tcpip.h>
#include <iostream>

// Link with ws2_32.lib
#pragma comment(lib, "Ws2_32.lib")

/* 
* RAW socket
* Future sniffer
*/


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


// UDP Header structure
typedef struct udp_hdr {
    unsigned short source port;
    unsigned short dest_port;
    unsigned short udp_len;
    unsigned short udp_sum;
} UDP_HDR;


void ShowError();
int main() {

    // Create s socket structure and initialize socket
    WSADATA wsaData;
    if (WSAStartup(0x0202, &wsaData)) { 
        ShowError(); 
        return 1;
    } 
    std::cout << "WSAStartup - OK" << std::endl;

    // Initialize socket
    SOCKET sckt;
    sckt = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
    if (sckt == INVALID_SOCKET) {
        ShowError();
        return 2;
    }
    std::cout << "Raw scoket is created" << std::endl;

    // Set socket options
    BOOL opt = TRUE;
    if (setsockopt(sckt, IPPROTO_IP, IP_HDRINCL, (char*)&opt, sizeof(opt)) == SOCKET_ERROR) {
        ShowError();
        return 3;
    }




    // Close socket
    if (closesocket(sckt) == SOCKET_ERROR) { 
        ShowError(); 
        return 33;
    }

    // Close and cleanup socket
    if (WSACleanup()) 
    { 
        ShowError(); 
        return 44;
    }
    std::cout << "WSACleanup - OK" << std::endl;
    return 0;
}


// Error function
void ShowError() {
	LPVOID lpMsgBuf = NULL;
    FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM, NULL, WSAGetLastError(),
        MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), (LPTSTR)&lpMsgBuf, 0, NULL);
    std::cout << (LPCTSTR)lpMsgBuf << std::endl;
    LocalFree(lpMsgBuf);
}




