
#include <winsock2.h>
#include <Ws2tcpip.h>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string>

#include <windows.h>

// Link with ws2_32.lib
#pragma comment(lib, "Ws2_32.lib")

/*
* RAW socket
* Client socket
* Future sniffer
*/


// Global variables
int BUF_LENGTH = 4096;
int MESSAFE_LENGTH = 4068;
//char* SOURCE_IP = (char*)"10.10.10.1";
//char* DEST_IP = (char*)"10.10.10.2";
//int SOURCE_PORT = 3004;
//int DEST_PORT = 4004;
char* SOURCE_IP = (char*)"locahost";
char* DEST_IP = (char*)"172.20.10.3";
int SOURCE_PORT = 443;
int DEST_PORT = 56421;


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
    unsigned short source_port;
    unsigned short dest_port;
    unsigned short udp_len;
    unsigned short udp_sum;
} UDP_HDR;


void ShowError();
USHORT checksum(USHORT* buffer, int size);
int __cdecl main() {

    // Create variables
    WSADATA wsaData;            // The containing socket data strucure
    struct sockaddr_in remote;  // The structure creating address and port for AF_INET 
    IP_HDR ipHdr;
    UDP_HDR udpHdr;
    unsigned short iTotalSize, iIPSize, iUdpSize, iUdpChecksumSize, ver;
    char buf[BUF_LENGTH], * ptr, szMessage[MESSAFE_LENGTH];
    in_addr ip_to_num;

    // Message to send and receive
    //strcpy(szMessage, "This message is for test only!!!");
    strncpy_s(szMessage, MESSAFE_LENGTH, "This message is for test only!!!", 33);

    // Initialize socket
    if (WSAStartup(MAKEWORD(2, 2), &wsaData)) {
        ShowError();
        return 1;
    }
    std::cout << "WSAStartup - OK" << std::endl;

    // Initialize socket
    SOCKET sckt;
    sckt = WSASocketW(AF_INET, SOCK_RAW, IPPROTO_UDP, NULL, 0, 0);
    if (sckt == INVALID_SOCKET) {
        ShowError();
        WSACleanup();
        return 2;
    }
    std::cout << "Raw scoket is created" << std::endl;

    // Set socket options
    BOOL opt = TRUE;
    if (setsockopt(sckt, IPPROTO_IP, IP_HDRINCL, (char*)&opt, sizeof(opt)) == SOCKET_ERROR) {
        ShowError();
        WSACleanup();
        return 3;
    }
    std::cout << "Setsockopt - OK" << std::endl;

    // Filling IP structure with data
    iTotalSize = sizeof(ipHdr) + sizeof(udpHdr) + strlen(szMessage); // The IP package length    
    iIPSize = sizeof(ipHdr) / sizeof(unsigned long);                 // ???    
    ver = 4;                                                         // For IP version is 4   
    ipHdr.ip_verlen = ver << 4;                                      // Create 1-st - char (containing version and header length) 0100 << 4 = 0100 0000 (1 char)
    ipHdr.ip_tos = 0;                                                // Create 2-nd - char (type of service)
    ipHdr.ip_total_len = htons(iTotalSize);                          // Create 3-rd - short (convert u_short into bytes row) (total length)
    ipHdr.ip_id = 0;                                                 // Create 4-th - short (ID)
    ipHdr.ip_offset = 0;                                             // Create 5-th - short (contains flags and offset)
    ipHdr.ip_ttl = 128;                                              // Create 6-th - char (contains time to live)
    ipHdr.ip_protocol = IPPROTO_UDP;                                 // Create 7-th - char (contains protocol type - TCP/UDP etc.)
    ipHdr.ip_checksum = 0;                                           // Create 8-th - short (checksum)
    ipHdr.sourceIP = inet_pton(AF_INET, SOURCE_IP, &ip_to_num);      // Create 9-th - int (source IP) (turn string into unsigned long - correct IPv4 address)
    ipHdr.destIP = inet_pton(AF_INET, DEST_IP, &ip_to_num);          // Create 10-th - int (destination IP) (turn string into unsigned long - correct IPv4 address)

    // Filling UDP structure with data
    iUdpSize = sizeof(udpHdr) + strlen(szMessage);                   // The UDP package length
    udpHdr.source_port = htons(SOURCE_PORT);                         // Create 1-st - char (source port)
    udpHdr.dest_port = htons(DEST_PORT);                             // Create 2-nd - char (destination port)
    udpHdr.udp_len = htons(iUdpSize);                                // Create 3-rd - char (convert u_short into bytes row) (UDP packet total length)
    udpHdr.udp_sum = 0;                                              // Сreate 4-tр - char (checksum)

    // !!!!!! Define the UDP checksum !!!!!!!!!!!!
    // Copy source IP address to the buffer and shift pointer to the end of the buffer
    iUdpChecksumSize = 0;
    ptr = buf;                                                       // Shift pointer into the start of the buffer once more
    ZeroMemory(buf, BUF_LENGTH);                                     // Fill the bock of memory (pointed by buf) with zeroes
    memcpy(ptr, &ipHdr.sourceIP, sizeof(ipHdr.sourceIP));            // Copy source IP into buffer
    ptr += sizeof(ipHdr.sourceIP);                                   // Shift pointer to the end of the buffer
    iUdpChecksumSize += sizeof(ipHdr.sourceIP);                      // Change UDP checksum

    // Copy destination IP address to the buffer and shift pointer to the end of the buffer    
    memcpy(ptr, &ipHdr.destIP, sizeof(ipHdr.destIP));                // Copy destination IP into buffer
    ptr += sizeof(ipHdr.destIP);                                     // Shift pointer to the end of the buffer
    ptr++;                                                           // Shift pointer by one byte (one char) (zero remains!!)
    iUdpChecksumSize += 1;                                           // Change UDP checksum once more

    // Copy protocol type (TCP/UDP etc.) into buffer and shift pointer to the end of the buffer
    memcpy(ptr, &ipHdr.ip_protocol, sizeof(ipHdr.ip_protocol));      // Copy protocol type (TCP/UDP etc.) into buffer
    ptr += sizeof(ipHdr.ip_protocol);                                // Shift pointer to the end of the buffer
    iUdpChecksumSize += sizeof(ipHdr.ip_protocol);                   // Change UDP checksum once more

    // Copy UDP length into buffer and shift pointer to the end of the buffer
    memcpy(ptr, &udpHdr.udp_len, sizeof(udpHdr.udp_len));            // Copy UDP length into buffer
    ptr += sizeof(udpHdr.udp_len);                                   // Shift pointer to the end of the buffer
    iUdpChecksumSize += sizeof(udpHdr.udp_len);                      // Change UDP checksum once more

    // Copy UDP header into the buffer and PUT THE FINAL UDP checksum to the UDP struct !!!!!
    memcpy(ptr, &udpHdr, sizeof(udpHdr));                            // Copy UDP header into the buffer
    ptr += sizeof(udpHdr);                                           // Shift pointer to the end of the buffer
    iUdpChecksumSize += sizeof(udpHdr);                              // Change UDP checksum once more
    for (unsigned int i = 0; i < strlen(szMessage); i++, ptr++)
        *ptr = szMessage[i];                                         // Using loop copy message letters into the buffer and shift pointer by 1 char at one time
    iUdpChecksumSize += strlen(szMessage);                           // Change UDP checksum once more
    udpHdr.udp_sum = checksum((USHORT*)buf, iUdpChecksumSize);       // !!!!! PUT THE FINAL UDP checksum to the UDP struct !!!!!
    // !!!! We finished the UDP checksum definition !!!!!

    // Fill the bock of memory (pointed by buf) with zeroes and shift pointer into the start of the buffer
    ZeroMemory(buf, BUF_LENGTH);                                     // Fill the buffer by zeroes (we do not need it any more!!!)
    ptr = buf;                                                       // Shift pointer into the start of the buffer once more

    // Copy headers and message into the buffer
    memcpy(ptr, &ipHdr, sizeof(ipHdr));                              // Copy IP header struct into the buffer
    ptr += sizeof(ipHdr);                                            // Shift pointer to the end of the buffer
    memcpy(ptr, &udpHdr, sizeof(udpHdr));                            // Copy UDP header struct into the buffer
    ptr += sizeof(udpHdr);                                           // Shift pointer to the end of the buffer
    memcpy(ptr, szMessage, strlen(szMessage));                       // Copy message into the buffer

    // Fill the structure creating address and port by data (IP address and port)    
    remote.sin_family = AF_INET;
    remote.sin_port = htons(DEST_PORT);
    remote.sin_addr.s_addr = inet_pton(AF_INET, DEST_IP, &ip_to_num);

    // Send data from buffer (IP header, UDP header and message)
    if (sendto(sckt, buf, iTotalSize, 0, (SOCKADDR*)&remote, sizeof(remote)) == SOCKET_ERROR) {
        ShowError();
        WSACleanup();
        closesocket(sckt);
        return 4;
    }
    std::cout << "sendto - OK" << std::endl;

    // Close socket
    if (closesocket(sckt) == SOCKET_ERROR) {
        ShowError();
        return 5;
    }

    // Close and cleanup socket
    if (WSACleanup())
    {
        ShowError();
        return 6;
    }
    std::cout << "WSACleanup - OK" << std::endl;
    return 0;
}


// Error function
void ShowError() {
    LPVOID lpMsgBuf = NULL;
    FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM, NULL, WSAGetLastError(),
        MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), (LPTSTR)&lpMsgBuf, 0, NULL);
    CharToOemA((char*)lpMsgBuf, (char*)lpMsgBuf);
    std::cout << (LPCTSTR)lpMsgBuf << std::endl;
    LocalFree(lpMsgBuf);
}
//CharToOemA((LPCSTR)lpMsgBuf, (LPSTR)lpMsgBuf);
//CharToOemW((LPCWSTR)lpMsgBuf, (LPSTR)lpMsgBuf);
//CharToOemBuffA((LPCSTR)lpMsgBuf, (LPSTR)lpMsgBuf, sizeof(lpMsgBuf));


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

