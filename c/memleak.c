#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <signal.h>
#include <unistd.h>

#define MEMORY_SIZE (100 * 1024 * 1024)

void event_sighandler(int s)
{
    exit(0);
}

void event_memleak(int s) {
    char *ptr = malloc(MEMORY_SIZE);
    if (ptr == NULL) {
        printf("oom!");
        return;
    }
    memset(ptr, 1 , MEMORY_SIZE);
}

int main() {
    signal(SIGINT, event_sighandler);
    signal(SIGTERM, event_sighandler);
    signal(SIGUSR1, event_memleak);
    
    while (1) {
        sleep(1);
    }

    return 0;
}
