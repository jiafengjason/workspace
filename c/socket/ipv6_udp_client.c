#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <string.h>
#include <netdb.h>
#include <netinet/in.h>
#include <net/if.h>
#include <sys/ioctl.h>

#define SERVPORT 3333
#define MAXDATASIZE 100

int main(int argc,char *argv[]) {
    int sockfd,sendbytes;
    char buf[MAXDATASIZE];
    struct hostent* host;
    struct sockaddr_in6 serv_addr;
    struct ifreq req;
    
    if(argc < 2) {//需要用户指定链接的地址
        fprintf(stderr,"Please enter the server's hostname");
        exit(1);
    }

    /*
    if((host = gethostbyname(argv[1])) == NULL) {//转换为hostent
        perror("gethostbyname");
        exit(1);
    }
    */

    if((sockfd = socket(AF_INET6,SOCK_DGRAM,0)) == -1) {//创建socket
        perror("socket");
        exit(1);
    }

    strcpy(req.ifr_name,"ens192");
    if (ioctl(sockfd,SIOCGIFINDEX, &req) < 0) {
        perror("siocgifindex");
        return -2;
    }
    fprintf(stderr,"scope_id: %d", req.ifr_ifindex);

    //填充数据
    serv_addr.sin6_family = AF_INET6;
    serv_addr.sin6_port = htons(SERVPORT);
    //serv_addr.sin6_scope_id = req.ifr_ifindex;
    inet_pton(AF_INET6, (char *)argv[1], &serv_addr.sin6_addr);

    if((sendbytes = sendto(sockfd,"hello",5,0,(struct sockaddr *)&serv_addr, sizeof(serv_addr))) == -1) {//发送消息给服务器端
        perror("send");
        exit(1);
    }

    close(sockfd);

}