#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BUF_SIZE 1024

int main() {
    int sockfd[2];
    unsigned char buffer1[BUF_SIZE], buffer2[BUF_SIZE];
    memset(buffer1, 0xab, sizeof(buffer1));
    memset(buffer2, 0xcd, sizeof(buffer2));

    if (socketpair(AF_UNIX, SOCK_STREAM, 0, sockfd) == -1) {
        perror("Error creating socket pair");
        return -1;
    }

    pid_t pid = fork();

    if (pid == -1) {
        perror("Error forking");
        return -1;
    }

    if (pid == 0) {
        // 子进程 (发送方)
        close(sockfd[0]);  // 关闭子进程中不需要的读端

        // 打开文件并获取文件描述符
        int file_descriptor = open("example.txt", O_RDONLY);
        if (file_descriptor == -1) {
            perror("Error opening file");
            return -1;
        }

        // 准备消息
        struct iovec iov[1];
        iov[0].iov_base = buffer1;
        iov[0].iov_len = sizeof(buffer1);

        char control_data[CMSG_SPACE(sizeof(int))];
        struct msghdr message = {0};
        message.msg_iov = iov;
        message.msg_iovlen = 1;
        message.msg_control = control_data;
        message.msg_controllen = sizeof(control_data);

        // 构建控制信息头部
        struct cmsghdr *cmsg = CMSG_FIRSTHDR(&message);
        cmsg->cmsg_len = CMSG_LEN(sizeof(int));
        cmsg->cmsg_level = SOL_SOCKET;
        cmsg->cmsg_type = SCM_RIGHTS;

        // 将文件描述符复制到辅助数据中
        *((int *)CMSG_DATA(cmsg)) = file_descriptor;

        // 发送消息
        if (sendmsg(sockfd[1], &message, 0) == -1) {
            perror("Error sending message");
            close(file_descriptor);
            return -1;
        }

        close(file_descriptor);  // 不再需要文件描述符

        close(sockfd[1]);  // 关闭写端
    } else {
        // 父进程 (接收方)
        close(sockfd[1]);  // 关闭父进程中不需要的写端

        struct iovec iov[1];
        iov[0].iov_base = buffer2;
        iov[0].iov_len = sizeof(buffer2);

        char control_data[CMSG_SPACE(sizeof(int))];
        struct msghdr message = {0};
        message.msg_iov = iov;
        message.msg_iovlen = 1;
        message.msg_control = control_data;
        message.msg_controllen = sizeof(control_data);

        // 接收消息
        if (recvmsg(sockfd[0], &message, 0) == -1) {
            perror("Error receiving message");
            return -1;
        }
        printf("buffer2[0]~buffer2[4] = %x %x %x %x\n", buffer2[0], buffer2[1], buffer2[2], buffer2[3]);
        // 从辅助数据中获取文件描述符
        struct cmsghdr *cmsg = CMSG_FIRSTHDR(&message);
        int received_fd;
        memcpy(&received_fd, CMSG_DATA(cmsg), sizeof(int));

        // 读取文件内容
        printf("Received file descriptor: %d\n", received_fd);
        ssize_t bytes_read = read(received_fd, buffer1, sizeof(buffer1));
        if (bytes_read == -1) {
            perror("Error reading file");
            return -1;
        }
        // 打印文件内容
        printf("Received data from file: %.*s\n", (int)bytes_read, buffer1);

        close(received_fd);  // 关闭接收到的文件描述符
        close(sockfd[0]);    // 关闭读端
    }

    return 0;
}