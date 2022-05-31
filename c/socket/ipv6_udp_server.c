#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <string.h>
#include <netinet/in.h>
#define SERVPORT 3333//定义端口号
#define BACKLOG 10//请求队列中允许的最大请求数
#define MAXDATASIZE 5//数据长度

int main(int argc,char *argv[]) {
    struct sockaddr_in6 server_sockaddr,client_sockaddr;//声明服务器和客户端的socket存储结构
    int sin_size,recvbytes;
    int sockfd,client_fd;//socket描述符
    char buf[MAXDATASIZE];//传输的数据
    socklen_t addr_len;

    if((sockfd = socket(AF_INET6,SOCK_DGRAM,0)) == -1) {//建立socket链接
        perror("Socket");
        exit(1);
    }

    printf("Socket success!,sockfd=%d\n",sockfd);

    /*
    int result = setsockopt(sockfd,SOL_SOCKET,SO_BINDTODEVICE,"ens192",sizeof("ens192"));
    if (result == -1) 
    {
        printf("setsockopt fail,errno: %d ,%s \n",errno,strerror(errno));
    }
    */
    
    //以sockaddt_in结构体填充socket信息
    server_sockaddr.sin6_family = AF_INET6;//IPv6
    server_sockaddr.sin6_port = htons(SERVPORT);//端口
    //地址使用通配符
    server_sockaddr.sin6_addr = in6addr_any;
    //inet_pton(AF_INET6, (char *)argv[1], &server_sockaddr.sin6_addr);//本主机的任意IP都可以使用

    if((bind(sockfd,(struct sockaddr *)&server_sockaddr,sizeof(struct sockaddr_in6))) == -1) {//bind函数绑定
        perror("bind");
        exit(-1);
    }

    printf("bind success!\n");

    //recvfrom(sockfd,buf,MAXDATASIZE,0,(struct sockaddr *)&client_sockaddr,addr_len))
    if((recvbytes = recv(sockfd,buf,MAXDATASIZE,0)) == -1) {//接收客户端的请求
        perror("recv");
        exit(1);
    }

    printf("received a connection : %s\n",buf);
    close(sockfd);

}