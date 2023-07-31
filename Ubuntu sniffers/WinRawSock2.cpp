#include <iostream>
#include <string>
using namespace std;

#ifdef _WIN32
//
#elif __linux__
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#endif


void error(const char *msg);
int main() {
	int sock;
	struct sockaddr_in addr;
	struct msghdr msg;

	msg.msg_iov = new struct iovec[100];
	msg.msg_iovlen = 100;

	addr.sin_family = AF_INET;
	addr.sin_port = 0;
	addr.sin_addr.s_addr = 0;

	sock = socket(AF_PACKET, SOCK_RAW, IPPROTO_IP);
	if (sock < 0) {
		error("Error openning cocket!!!");
	}

	cout << bind(sock, (struct sockaddr*)&addr, sizeof(addr)) << endl;
	cout << errno << endl;

	cout << recvmsg(sock, &msg, 0) << endl;
	cout << errno << endl;
	return 0;
}


void error(const char *msg)
{
    perror(msg);
    exit(1);
}