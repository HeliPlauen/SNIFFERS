#include "header.h"
#include <iostream>
using namespace std;


/* open raw socket, set promiscuous mode */
void init_net() {

	WSADATA w;
	SOCKADDR_IN sa;
	DWORD bytes;
	char hostname[HOSTNAME_LEN];
	struct hostent* h;
	unsigned int opt = 1;

	if (WSAStartup(MAKEWORD(2, 2), &w) != 0)
		die("WSAStartup failed\n");

	if ((s0k = socket(AF_INET, SOCK_RAW, IPPROTO_IP)) == INVALID_SOCKET)
		die("unable to open raw socket\n");

	// use default interface
	if ((gethostname(hostname, HOSTNAME_LEN)) == SOCKET_ERROR)
		die("unable to gethostname\n");

	if ((h = gethostbyname(hostname)) == NULL)
		die("unable to gethostbyname\n");

	sa.sin_family = AF_INET;
	sa.sin_port = htons(6000);
	memcpy(&sa.sin_addr.S_un.S_addr, h->h_addr_list[0], h->h_length);

	if ((bind(s0k, (SOCKADDR*)&sa, sizeof(sa))) == SOCKET_ERROR)
		die("unable to bind() socket\n");

	if (promiscuous)	/* -d on the command line to disable promiscuous mode */
		if ((WSAIoctl(s0k, SIO_RCVALL, &opt, sizeof(opt), NULL, 0, &bytes, NULL, NULL)) == SOCKET_ERROR)
			die("failed to set promiscuous mode\n");
}


int main() {

	char pak[PAKSIZE];
	DWORD bytes;
	init_net();

	WriteData("Program has started: ");
	WriteData("\r\n\r\n");

	while (1)
	{
		memset(pak, 0, sizeof(pak));
		if ((bytes = recv(s0k, pak, sizeof(pak), 0)) == SOCKET_ERROR)
		{
			die("socket error on recv\n");
			return 1;
		}
		else {
			process_pak(pak, bytes);
		}
	}
	return 0;
}


void WriteData(const char* buffer)
{
	FILE* pFile;
	pFile = fopen("./File1.txt", "a");
	printf(buffer);
	fprintf(pFile, buffer);
	fclose(pFile);
}


/* parse pak, print out requested fields */
void process_pak(char* pak, int len) {

	struct iphdr* ip;
	struct tcphdr* tcp;
	char* data;
	unsigned char proto;	/* to avoid repeated dereferencing */
	int i, j, k, end, datasize;

	ip = (struct iphdr*)pak;
	proto = ip->proto;

	printf("Prototype: %i\n", (unsigned char)proto);

	if (proto == IPPROTO_TCP)
	{
		tcp = (struct tcphdr*)(pak + (ip->ihl * 4));

		data = pak + (ip->ihl * 4) + (tcp->tcphl * 4);
		datasize = ntohs(ip->totlen) - (ip->ihl * 4) - (tcp->tcphl * 4);

		/* ==================================== */
		/*       START CONTROLE FUNCTIE         */
		/* ==================================== */

		i = 0;
		// If the packet size is smaller than the required size, just trow it away!
//		if( datasize < minSize )
//		{
//			return;
//		}

		char temp[50];
		sprintf(temp, "New Package: %x %x %x %x", data[0], data[1], data[2], data[3]);
		WriteData(temp);
		WriteData("\r\n");

		printf("DataSize: %i\r\n", datasize);

		// Print all data to the file.
		for (j = 0; j < datasize; j++)
		{
			char temp[10];
			sprintf(temp, "%4i", data[j]);

			WriteData(temp);
			i = (i + 1);
			if (i == 4) { WriteData("  "); }
			if (i == 8) { WriteData("    "); }
			if (i == 12) { WriteData("  "); }
			if (i == 16) {
				WriteData("     ->     ");
				i = 0;
				for (k = (j - 15); k < (j + 1); k++)
				{
					char temp[10];
					sprintf(temp, "%1c", data[k]);
					if (data[k] < 32)
					{
						sprintf(temp, "%1c", '.');
					}

					WriteData(temp);
					i = (i + 1);
					if (i == 8) { WriteData("  "); }
				}
				WriteData("\r\n"); i = 0;
			}
		}
		if (i > 0)

			WriteData("\r\n");
		WriteData("\r\n");

	}
	else {
		// No TCP protocol: return and don't waist any time!
		return;
	}
}


void bind_to_interface(int choice) {

	SOCKET sd;
	sd = WSASocket(AF_INET, SOCK_DGRAM, 0, 0, 0, 0);
	if (sd == SOCKET_ERROR)
		printf("error on WSASocket\n");

	INTERFACE_INFO InterfaceList[20];
	unsigned long nBytesReturned;
	if (WSAIoctl(sd, SIO_GET_INTERFACE_LIST, 0, 0, &InterfaceList, sizeof(InterfaceList), &nBytesReturned, 0, 0) == SOCKET_ERROR) {
		printf("error fetching interface list\n");
	}

	int nNumInterfaces = nBytesReturned / sizeof(INTERFACE_INFO);
	if (choice > nNumInterfaces) {
		die("invalid interface selection\n");
	}

	if (choice) {
		// bind to the specified interface and return
		SOCKADDR_IN* pAddress;
		pAddress = (SOCKADDR_IN*)&(InterfaceList[choice - 1].iiAddress);
		printf("using interface: %s\n", inet_ntoa(pAddress->sin_addr));

		if ((bind(s0k, (SOCKADDR*)&(InterfaceList[choice - 1].iiAddress), sizeof(SOCKADDR_IN))) == SOCKET_ERROR)
			die("unable to bind() socket\n");

		return;
	}
}


void die(const char* s) {
	printf(s);
	WSACleanup();
	WriteData("%s");
	exit(-1);
}