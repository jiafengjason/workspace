#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/fanotify.h>

#define EVENT_SIZE  (sizeof(struct fanotify_event_metadata) + 256)
#define EVENT_BUF_LEN     (10 * EVENT_SIZE)

int main(int argc, char *argv[]) {
    int fanotify_fd;
    ssize_t len;
    char buf[EVENT_BUF_LEN];
    struct fanotify_event_metadata *metadata;

    // 打开fanotify文件描述符
    fanotify_fd = fanotify_init(FAN_CLOEXEC | FAN_CLASS_CONTENT, O_RDONLY | O_LARGEFILE);
    if (fanotify_fd == -1) {
        perror("fanotify_init");
        exit(EXIT_FAILURE);
    }

    // 添加要监视的目录或文件
    if (fanotify_mark(fanotify_fd, FAN_MARK_ADD | FAN_MARK_MOUNT, FAN_DELETE, AT_FDCWD, argv[1]) == -1) {
        perror("fanotify_mark");
        exit(EXIT_FAILURE);
    }

    printf("Monitoring directory: %s\n", argv[1]);

    while (1) {
        // 读取事件
        len = read(fanotify_fd, buf, EVENT_BUF_LEN);
        if (len == -1 && errno != EAGAIN) {
            perror("read");
            exit(EXIT_FAILURE);
        }

        // 处理事件
        for (char *ptr = buf; ptr < buf + len; ptr += sizeof(struct fanotify_event_metadata) + metadata->event_len) {
            metadata = (struct fanotify_event_metadata *)ptr;
            if (metadata->mask & FAN_DELETE) {
                printf("File deleted: %s\n", metadata->pathname);
            }
        }
    }

    close(fanotify_fd);
    return 0;
}

