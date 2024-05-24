#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>

void send_message(int sockfd, const char* message) {
    send(sockfd, message, strlen(message), 0);
}

void receive_message(int sockfd, char* buffer, size_t buffer_size) {
    ssize_t received_bytes = recv(sockfd, buffer, buffer_size - 1, 0);
    if (received_bytes > 0) {
        buffer[received_bytes] = '\0';  // Null-terminate the received data
        printf("Received: %s\n", buffer);
    } else {
        perror("Error receiving message");
    }
}

int main() {
    int sv[2];

    if (socketpair(AF_UNIX, SOCK_STREAM, 0, sv) == -1) {
        perror("Error creating socket pair");
        return -1;
    }

    pid_t pid = fork();

    if (pid == -1) {
        perror("Error forking");
        return -1;
    }

    if (pid == 0) {// 子进程
        close(sv[0]);
        char buffer[1024];
        receive_message(sv[1], buffer, sizeof(buffer));
        send_message(sv[1], "get a message from father");
        close(sv[1]);  // 关闭写端
    } else {// 父进程
        close(sv[1]);
        send_message(sv[0], "123");
        char buffer[1024];
        receive_message(sv[0], buffer, sizeof(buffer));
        close(sv[0]);  // 关闭读端
    }
    return 0;
}