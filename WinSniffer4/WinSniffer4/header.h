#pragma once

#pragma comment(lib, "ws2_32.lib")

#include <winsock2.h>
#include <stdio.h>
#include <string.h>
#include <windows.h>
#include <ws2tcpip.h>
#include <time.h>

/* packet header structures */
struct iphdr {
	unsigned char ihl : 4;
	unsigned char ver : 4;

	unsigned char tos;
	unsigned short totlen;
	unsigned short id;
	unsigned short frag_and_flags;
	unsigned char ttl;
	unsigned char proto;
	unsigned short checksum;
	unsigned int src;
	unsigned int dst;
};

struct tcphdr {
	unsigned short sport;
	unsigned short dport;
	unsigned int   seq;
	unsigned int   acknum;
	unsigned char  unused : 4;
	unsigned char  tcphl : 4;
	unsigned char  Flags;
	unsigned short Windows;
	unsigned short cksum;
	unsigned short UrgPointer;
};

#define HOSTNAME_LEN 1024
#define SIO_RCVALL _WSAIOW(IOC_VENDOR,1)
#define PAKSIZE 65536

// Use deprecated functions
#pragma warning(disable : 4996)

void init_net(void);
void die(const char*);
void process_pak(char*, int);
void bind_to_interface(int);
void WriteData(const char*);

/* G L O B A L S */
SOCKET s0k;
short promiscuous = 1;
int minSize = 30;

unsigned char NavyFieldHDR[48] =
{ 4,   3,   2,   1 };


// Pin Code versturen
// 04 03 02 01 01 61 01 80  00 00 00 00 00 00 00 00
// 04 00 00 00 XX XX XX XX  CC OO DD EE