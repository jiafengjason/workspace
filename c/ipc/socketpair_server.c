#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
  
int main() {
    int sv[2];
    pid_t pid;

    // 创建一个socketpair
    if (socketpair(AF_UNIX, SOCK_STREAM, 0, sv) == -1) {
        perror("socketpair");
        exit(EXIT_FAILURE);
    }

    printf("%d %d\n", sv[0], sv[1]);

    // 假设我们要启动另一个进程（不是通过fork）并传递其中一个文件描述符
    // 这里我们只是简单模拟，实际上你可能会通过其他方式（如IPC, 文件, 环境变量等）来传递文件描述符  

    // 写入数据到socketpair的一个套接字
    const char *msg = "Hello from process A!";
    write(sv[1], msg, strlen(msg) + 1);

    while (1) {
        sleep(1);
    }

    // 关闭我们的文件描述符，因为另一个进程会读取它
    close(sv[1]);

    // 等待或进行其他操作
    return 0;
}