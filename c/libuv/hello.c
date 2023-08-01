//gcc -o hello hello.c -luv

#include <uv.h>

uv_loop_t loop;
uv_timer_t timeout;
uv_thread_t thread;
uv_async_t async;

void timer_cb(uv_timer_t* handle) {
    printf("Hello, world!\n");
    printf("uv version:%s\n", uv_version_string());
}

void async_cb(uv_async_t* handle)
{
    printf("async running!\n");
    uv_timer_init(&loop, &timeout);
    uv_timer_start(&timeout, timer_cb, 1000, 5000);
}

void hello_run(void *arg) 
{
    printf("hello running, send async!\n");

    uv_async_send((uv_async_t*)arg);
}

int main() {
    uv_loop_init(&loop);

    uv_async_init(&loop, &async, async_cb);
    uv_thread_create(&thread, hello_run, &async);
    uv_run(&loop, UV_RUN_DEFAULT);

    uv_thread_join(&thread);
    uv_loop_close(&loop);

    return 0;
}

