#define WIN32_LEAN_AND_MEAN

#include <winsock2.h>
#include <Ws2tcpip.h>
#include <stdio.h>

#include <iostream>
#include <string>

/*
* Client
* Server
* Getting FILES
* Made changes using HABR article
*/

// Link with ws2_32.lib
#pragma comment(lib, "Ws2_32.lib")

#define DEFAULT_BUFLEN 1024       // The buffer for download
#define DEFAULT_PORT "443"        // The port listen to
#define DEFAULT_PORT_2 "9090"     // The port for sending reports
#define URL "127.0.0.1"


int ListenSocketFunc(int iResult_2, SOCKET ConnectSocket_2);
int __cdecl main() {

    //----------------------
    // Declare and initialize variables.
    WSADATA wsaData;
    int iResult;

    WSADATA wsaData_2;
    int iResult_2;

    SOCKET ListenSocket = INVALID_SOCKET;
    SOCKET ConnectSocket_2 = INVALID_SOCKET;

    struct sockaddr_in service;
    ZeroMemory(&service, sizeof(service));

    struct sockaddr_in clientService_2;
    ZeroMemory(&clientService_2, sizeof(clientService_2));
    
    char recvbuf[DEFAULT_BUFLEN];
    int recvbuflen = DEFAULT_BUFLEN;

    //----------------------
    // Initialize Winsock
    iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
    printf("iResult (Inintializing): %i.\n", iResult);
    if (iResult != NO_ERROR) {
        printf("WSAStartup server failed: %d\n", iResult);
        return 1;
    }

    iResult_2 = WSAStartup(MAKEWORD(2, 2), &wsaData_2);
    printf("iResult_2 (Inintializing): %i.\n", iResult_2);
    if (iResult_2 != NO_ERROR) {
        printf("WSAStartup client failed: %d\n", iResult_2);
        return 1; 
    }    

    //----------------------
    // Create a SOCKET for connecting to server (SOCK_STREAM??? IPPROTO_TCP???) !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ListenSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    printf("ListenSocket: %llu\n", ListenSocket);
    if (ListenSocket == INVALID_SOCKET) {
        printf("Error at server socket(): %i\n", WSAGetLastError());
        WSACleanup();
        return 2;
    }

    ConnectSocket_2 = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    printf("ConnectSocket_2: %llu\n", ConnectSocket_2);
    if (ConnectSocket_2 == INVALID_SOCKET) {
        printf("Error at client socket(): %i\n", WSAGetLastError());
        WSACleanup();
        return 2;
    }    

    //----------------------
    // The sockaddr_in structure specifies the address family,
    // IP address, and port of the server to be connected to.
    in_addr ip_to_num;
    iResult = inet_pton(AF_INET, URL, &ip_to_num);
    if (iResult < 0) {
        printf("Error in IP translation to special numeric format\n");
        WSACleanup();
        return 7;
    }
    service.sin_family = AF_INET;
    service.sin_addr = ip_to_num;
    service.sin_port = htons(atoi(DEFAULT_PORT)); 
    printf("service: %i, %lu, %i, %i .\n", AF_INET, service.sin_addr.s_addr, atoi(DEFAULT_PORT), service.sin_port);

    in_addr ip_to_num_2;
    iResult_2 = inet_pton(AF_INET, URL, &ip_to_num_2);
    if (iResult_2 < 0) {
        printf("Error in IP translation to special numeric format\n");
        WSACleanup();
        return 7;
    }
    clientService_2.sin_family = AF_INET;
    clientService_2.sin_addr = ip_to_num_2;
    clientService_2.sin_port = htons(atoi(DEFAULT_PORT_2));
    printf("clientService_2: %i, %lu, %i, %i .\n", AF_INET, clientService_2.sin_addr.s_addr, atoi(DEFAULT_PORT_2), clientService_2.sin_port);

    //----------------------
    // Create server - bind socket
    iResult = bind(ListenSocket, (SOCKADDR*)&service, sizeof(service));
    printf("iResult (Connecting): %i.\n", iResult);
    if (iResult == SOCKET_ERROR) {
        closesocket(ListenSocket);
        printf("Unable to connect to server: %i\n", WSAGetLastError());
        WSACleanup();
        return 3;
    }

    // Connect to server.
    iResult_2 = connect(ConnectSocket_2, (SOCKADDR*)&clientService_2, sizeof(clientService_2));
    printf("iResult_2 (Connecting): %i.\n", iResult_2);
    if (iResult_2 == SOCKET_ERROR) {
        closesocket(ListenSocket);
        closesocket(ConnectSocket_2);
        printf("Unable to connect to server: %i\n", WSAGetLastError());
        WSACleanup();
        return 3;
    }

    // Listen to socket
    iResult = listen(ListenSocket, SOMAXCONN);
    printf("iResult (Start listening): %i.\n", iResult);
    if (iResult != 0) {
        printf("Listen func failed with %i\n", WSAGetLastError());
        closesocket(ListenSocket);
        closesocket(ConnectSocket_2);
        WSACleanup();
        return 4;
    }

    // Accept socket
    int loop_counter = 0;
    while (true) {
        struct sockaddr_in service_2;
        ZeroMemory(&service_2, sizeof(service_2));
        int sizeof_sin = sizeof(service_2);
        SOCKET acceptSocket = accept(ListenSocket, (SOCKADDR*)&service_2, &sizeof_sin);
        // SOCKET acceptSocket = accept(ListenSocket, NULL, NULL);
        printf("iResult (Accept socket): %i.\n", iResult);

        if (acceptSocket == INVALID_SOCKET)
        {
            printf("Accept func failed with %i\n", WSAGetLastError());
            closesocket(acceptSocket);
            closesocket(ListenSocket);
            closesocket(ConnectSocket_2);
            WSACleanup();
            return 5;
        }

        // Receive until the peer closes the connection
        iResult_2 = 0;
        do {
            printf("Inside the loop!\n");
            iResult = recv(acceptSocket, recvbuf, recvbuflen, 0);   
            if (iResult > 0) {
                printf("Bytes received: %d\n", iResult);                

                // Get the number of bytes
                iResult_2 += iResult;
                char* filename = recvbuf;
                printf("File name: ");
                int i = 0;
                while (i < recvbuflen) {
                    char letter = *(filename + i);
                    if (letter == '\0' || letter == '\n') {
                        break;
                    }                    
                    printf("%c", letter);
                    i++;
                }
                printf("\n");

                // Call function starting client socket
                if (ListenSocketFunc(iResult_2, ConnectSocket_2) != 0) {
                    closesocket(acceptSocket);
                    closesocket(ListenSocket);
                    closesocket(ConnectSocket_2);
                    WSACleanup();
                    return 6;
                }
            }
            else if (iResult == 0) {
                printf("Connection closed\n");
                printf("Summary bytes received: %d\n", iResult_2);
            }
            else {
                printf("recv failed: %d\n", WSAGetLastError());
            }                
        } while (iResult > 0);

        closesocket(acceptSocket);
        loop_counter++;
        if (loop_counter == 5) {
            break;
        }
    }

    // cleanup
    closesocket(ListenSocket);
    closesocket(ConnectSocket_2);
    WSACleanup();
    printf("Finish receiving!!!\n");

    return 0;
}


int ListenSocketFunc(int iResult_2, SOCKET ConnectSocket_2) {
    std::string string_result = std::to_string(iResult_2);
    const char* char_arr_result = string_result.c_str();

    // Send an initial buffer    
    iResult_2 = send(ConnectSocket_2, char_arr_result, (int)strlen(char_arr_result), 0);

    if (iResult_2 == SOCKET_ERROR) {
        printf("send failed: %d\n", WSAGetLastError());
        //closesocket(ConnectSocket_2);
        //WSACleanup();
        return 1;
    }

    printf("Bytes Sent: %s\n", char_arr_result);
    return 0;
}