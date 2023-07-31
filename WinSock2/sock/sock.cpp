#define WIN32_LEAN_AND_MEAN

#include <winsock2.h>
#include <Ws2tcpip.h>
#include <stdio.h>
#include <string>


/*
* Server
* Getting string
*/


// Link with ws2_32.lib
#pragma comment(lib, "Ws2_32.lib")

#define DEFAULT_BUFLEN 1024       // The buffer for download
#define DEFAULT_PORT "443"        // The port listen to


int __cdecl main() {

    //----------------------
    // Declare and initialize variables.
    WSADATA wsaData;
    int iResult;


    SOCKET ListenSocket = INVALID_SOCKET;
    struct sockaddr_in service;
    
    char recvbuf[DEFAULT_BUFLEN];
    int recvbuflen = DEFAULT_BUFLEN;

    //----------------------
    // Initialize Winsock
    iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);

    int somethingfortest = int(MAKEWORD(2, 2));
    printf("MAKEWORD(2, 2): %i.\n",somethingfortest);
    printf("iResult (Inintializing): %i.\n", iResult);

    if (iResult != NO_ERROR) {
        printf("WSAStartup failed: %d\n", iResult);
        return 1;
    }

    //----------------------
    // Create a SOCKET for connecting to server
    ListenSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

    printf("ConnectSocket: %i\n", ListenSocket);

    if (ListenSocket == INVALID_SOCKET) {
        printf("Error at socket(): %ld\n", WSAGetLastError());
        WSACleanup();
        return 2;
    }

    //----------------------
    // The sockaddr_in structure specifies the address family,
    // IP address, and port of the server to be connected to.
    service.sin_family = AF_INET;
    service.sin_addr.s_addr = inet_addr("127.0.0.1");
    service.sin_port = htons(atoi(DEFAULT_PORT)); 

    printf("clientService: %i, %ul, %i, %i .\n", AF_INET, service.sin_addr.s_addr, atoi(DEFAULT_PORT), service.sin_port);

    //----------------------
    // Create server - bind socket
    iResult = bind(ListenSocket, (SOCKADDR*)&service, sizeof(service));
    printf("iResult (Connecting): %i.\n", iResult);

    // Listen to socket
    iResult = listen(ListenSocket, SOMAXCONN);
    printf("iResult (Start listening): %i.\n", iResult);

    if (iResult != 0) {
        printf("Listen func failed with %ld\n", WSAGetLastError());
        closesocket(ListenSocket);
        WSACleanup();
        return 4;
    }

    // Accept socket
    while (true) {
        int sizeof_sin = sizeof(service);
        SOCKET acceptSocket = accept(ListenSocket, (SOCKADDR*)&service, &sizeof_sin);
        // SOCKET acceptSocket = accept(ListenSocket, NULL, NULL);
        printf("iResult (Accept socket): %i.\n", iResult);

        if (acceptSocket == INVALID_SOCKET)
        {
            printf("Accept func failed with %ld\n", WSAGetLastError());
            closesocket(acceptSocket);
            WSACleanup();
            return 5;
        }

        // Receive until the peer closes the connection
        do {
            printf("Inside the loop!\n");
            iResult = recv(acceptSocket, recvbuf, recvbuflen, 0);
            if (iResult > 0)
                printf("Bytes received: %d\n", iResult);
            else if (iResult == 0)
                printf("Connection closed\n");
            else
                printf("recv failed: %d\n", WSAGetLastError());
        } while (iResult > 0);
    }

    // cleanup
    closesocket(ListenSocket);
    WSACleanup();
    printf("Finish receiving!!!\n");

    return 0;
}