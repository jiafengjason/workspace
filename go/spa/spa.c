//gcc -Iinclude -Llib -Wl,-rpath=lib -lfko -o spa spa.c -g
#include "fko.h"
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <errno.h>
#include <sys/socket.h>

int main()
{
	int res;
	res = fko_send_spa_data("192.168.188.56", "533,1,2" , "ffcbbd5d0ff16b8d161b80a8be26b918", 62201, "enlink");
	//res = fko_send_udp_data("127.0.0.1", 62201, "enlink", 6);
	printf("res:%d\n", res);
}
