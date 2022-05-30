#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <string.h>
#include <netdb.h>
#include <netinet/in.h>
#define SERVPORT 3333
#define MAXDATASIZE 100

int main(int argc,char *argv[]) {
    int sockfd,sendbytes;
    char buf[MAXDATASIZE];
    struct hostent* host;
    struct sockaddr_in serv_addr;

    if(argc < 2) {//需要用户指定链接的地址
        fprintf(stderr,"Please enter the server's hostname");
        exit(1);
    }

    if((host = gethostbyname(argv[1])) == NULL) {//转换为hostent
        perror("gethostbyname");
        exit(1);
    }

    if((sockfd = socket(AF_INET,SOCK_DGRAM,0)) == -1) {//创建socket
        perror("socket");
        exit(1);
    }

    //填充数据
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(SERVPORT);
    serv_addr.sin_addr = *((struct in_addr *)host->h_addr);
    //serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    bzero(&(serv_addr.sin_zero),8);

    if((sendbytes = sendto(sockfd,"hello",5,0,(struct sockaddr *)&serv_addr, sizeof(serv_addr))) == -1) {//发送消息给服务器端
        perror("send");
        exit(1);
    }

    close(sockfd);

}