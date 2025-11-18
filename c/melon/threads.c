#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "mln_thread_pool.h"

static int main_process_handler(void *data);
static int child_process_handler(void *data);
static void free_handler(void *data);

int main(int argc, char *argv[])
{
    struct mln_thread_pool_attr tpattr;

    tpattr.main_data = NULL;
    tpattr.child_process_handler = child_process_handler;
    tpattr.main_process_handler = main_process_handler;
    tpattr.free_handler = free_handler;
    tpattr.cond_timeout = 10;
    tpattr.max = 10;
    tpattr.concurrency = 10;
    return mln_thread_pool_run(&tpattr);
}

static int child_process_handler(void *data)
{
    printf("%s\n", (char *)data);
    return 0;
}

static int main_process_handler(void *data)
{
    int n;
    char *text;

    while (1) {
        if ((text = (char *)malloc(16)) == NULL) {
            return -1;
        }
        n = snprintf(text, 15, "hello world");
        text[n] = 0;
        mln_thread_pool_resource_add(text);
        usleep(1000);
    }
}

static void free_handler(void *data)
{
    free(data);
}
