#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <string.h>
#include <netdb.h>
#include <netinet/in.h>
#include <fcntl.h>

#define SERVPORT 10911
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

    if((sockfd = socket(AF_INET,SOCK_STREAM,IPPROTO_TCP)) == -1) {//创建socket
        perror("socket");
        exit(1);
    }

    //填充数据
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(SERVPORT);
    serv_addr.sin_addr = *((struct in_addr *)host->h_addr);
    bzero(&(serv_addr.sin_zero),8);

    fcntl(sockfd, F_SETFL, fcntl(sockfd, F_GETFL) | O_NONBLOCK);
    if((connect(sockfd,(struct sockaddr *)&serv_addr,sizeof(struct sockaddr))) == -1) {//发起对服务器的链接
        perror("connect");
        exit(1);
    }

    if((sendbytes = send(sockfd,"hello",5,0)) == -1) {//发送消息给服务器端
        perror("send");
        exit(1);
    }

    close(sockfd);

}
