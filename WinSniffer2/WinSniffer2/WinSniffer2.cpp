#include <winsock2.h>
#include <Ws2tcpip.h>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string>

// Link with ws2_32.lib
#pragma comment(lib, "Ws2_32.lib")


/*
* RAW socket
* Server socket
* Sniffer
* IP
*/


#define MAX_PACKET_SIZE 0x10000
#define SIO_RCVALL  _WSAIOW(IOC_VENDOR,1)
//#define SIO_RCVALL 0x98000001

typedef struct IPHeder {
    unsigned char version;
    unsigned char typeserv;
    unsigned short lenght;
    unsigned short id;
    unsigned short flag;
    unsigned char timelive;
    unsigned char protocol;
    unsigned short headersum;
    unsigned int sourceaddr;
    unsigned int destaddr;
    unsigned char data[];
} IPHeader; // Структура для вывода ip заголовка

int main() {
    WSADATA wsd;
    SOCKET s;
    HOSTENT* hst;
    SOCKADDR_IN saddr;
    IN_ADDR iaddr;
    char name[128];
    int err;
    IPHeader* header;

    err = WSAStartup(MAKEWORD(2, 2), &wsd); // Инициализация винсок
    if (err != 0) { // Проверка инициализации винсок
        printf("WinSock error\n");
        WSAGetLastError();
        WSACleanup();
        return 1;
    }
    else {
        printf("WinSock - OK\n");
    }

    s = socket(AF_INET, SOCK_RAW, IPPROTO_IP); // Инициализация сокета
    if (s == INVALID_SOCKET) { // Проверка сокета
        printf("Socket error", err);
        WSAGetLastError();
        WSACleanup();
        closesocket(s);
        return 2;
    }
    else {
        printf("Socket - OK\n");
    }


    err = gethostname(name, sizeof(name)); // Имя машины
    if (err) {
        printf("gethostname function failed %d\n", err);
        WSAGetLastError();
        WSACleanup();
        closesocket(s);
        return 3;
    }
    else {
        printf("Host name: %s\n", name);
    }

    hst = gethostbyname(name); // Адрес машины
    err = WSAGetLastError();
    if (err) {
        printf("gethostbyname function failed %d\n", err);
        WSAGetLastError();
        WSACleanup();
        closesocket(s);
        return 4;
    }
    else {
        printf("Host address: %s\n", hst);
        printf("Host address: %s\n", inet_ntoa(*((struct in_addr*)hst->h_addr_list[0])));
    }
    //memcpy(&saddr.sin_addr.s_addr, hst->h_addr_list[1], sizeof(saddr.sin_addr.s_addr)); // Имя хоста копируем в saddr
    ZeroMemory(&saddr, sizeof(saddr));
    saddr.sin_family = AF_INET; // Заполняем поля структуры saddr
    saddr.sin_addr.s_addr = ((struct in_addr*)hst->h_addr_list[0])->s_addr;

    err = bind(s, (SOCKADDR*)&saddr, sizeof(saddr)); // Привязка сокета
    if (err == SOCKET_ERROR) { // Проверка 
        printf("Bind error\n", err);
        WSAGetLastError();        
        WSACleanup();
        closesocket(s);
        return 5;
    }
    else {
        printf("Bind - OK\n");
    }

    unsigned long flag = 1;
    char buff[MAX_PACKET_SIZE]; // 
    err = ioctlsocket(s, SIO_RCVALL, &flag);
    if (err == SOCKET_ERROR) { // Проверка 
        printf("Bind error\n", err);
        WSAGetLastError();
        WSACleanup();
        closesocket(s);
        return 6;
    }
    else {
        printf("Promiscuous regime - OK\n");
    }

    BOOL opt = TRUE;
    if (setsockopt(s, SOL_SOCKET, SO_EXCLUSIVEADDRUSE, (char*)&opt, sizeof(opt)) == SOCKET_ERROR) {
        printf("Setsockopt error\n");
        WSACleanup();
        closesocket(s);
        return 7;
    }
    else {
        printf("Setsockopt - OK\n");
    } 
    
    int counter = 0;
    while (true) {
        err = recv(s, buff, sizeof(buff), 0);
        if (err == SOCKET_ERROR) {
            printf("Recv error", err);
            closesocket(s);
            WSACleanup();
            return 8;
        }
        else {
            // Get IP header
            header = (IPHeader*)buff;

            // Get source IP
            iaddr.s_addr = header->sourceaddr;
            printf("Source, %i\n", int(header->sourceaddr));
            printf("Source, %s\n", inet_ntoa(iaddr));

            // Get destination IP
            iaddr.s_addr = header->destaddr;
            printf("Destaddr, %i\n", int(header->destaddr));
            printf("Destaddr, %s\n", inet_ntoa(iaddr));

            // Get protocol
            printf("Protocol, %i\n", int(header->protocol));
            printf("-----------------------------------\n");
        }
        counter++;
        if (counter == 10) {
            break;
        }
    }
    closesocket(s);
    WSACleanup();
    return 0;
}