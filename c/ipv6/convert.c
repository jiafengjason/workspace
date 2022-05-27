#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

int main(void)
{
	char IPdotdec[20] = "6000::1";
	struct in6_addr s;

	inet_pton(AF_INET6, IPdotdec, (void *)&s);
	inet_ntop(AF_INET6, (void *)&s, IPdotdec, 16);

	printf("inet_ntop: %s\n", IPdotdec);
	return 0;
}
