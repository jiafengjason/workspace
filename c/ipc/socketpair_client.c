#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
  
int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <socket_fd>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    // 假设我们从进程A或其他方式获取了文件描述符
    int sock_fd = atoi(argv[1]);

    // 从socketpair读取数据
    char buffer[1024];
    ssize_t bytes_read = read(sock_fd, buffer, sizeof(buffer) - 1);
    if (bytes_read > 0) {
        buffer[bytes_read] = '\0'; // 确保字符串以null终止
        printf("Received: %s\n", buffer);
    } else {  
        perror("read");
    }

    // 关闭文件描述符
    close(sock_fd);

    return 0;
}