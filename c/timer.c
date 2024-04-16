//gcc -o timer timer.c -lrt
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <time.h>
#include <unistd.h>

// 定义一个结构体来存储回调函数及其参数
typedef struct {
    void (*callback)(void *arg);
    void *arg;
} TimerCallbackData;

// 包装函数，它将在信号处理器中调用  
static void timer_wrapper(int signum, siginfo_t *info, void *context) {
    TimerCallbackData *data = (TimerCallbackData *)info->si_value.sival_ptr;
    data->callback(data->arg);
}

// 实际的回调函数，它接受一个void指针参数  
void my_timer_callback(void *arg) {
    int *my_int = (int *)arg;
    printf("Timer expired. Value: %d\n", *my_int);
}

int main() {
    struct sigaction sa;
    struct sigevent sev;
    timer_t timerid;
    struct itimerspec its;
    TimerCallbackData callback_data;

    // 设置回调数据和回调函数
    int my_int = 42;
    callback_data.callback = my_timer_callback;
    callback_data.arg = &my_int;

    // 初始化信号处理器  
    sa.sa_flags = SA_SIGINFO;
    sa.sa_sigaction = timer_wrapper;
    sigemptyset(&sa.sa_mask);
    if (sigaction(SIGRTMIN, &sa, NULL) == -1) {
        perror("sigaction");
        exit(EXIT_FAILURE);
    }

    // 初始化sigevent结构，设置通知方式和回调函数数据
    sev.sigev_notify = SIGEV_SIGNAL;
    sev.sigev_signo = SIGRTMIN;
    sev.sigev_value.sival_ptr = &callback_data;

    // 创建定时器
    if (timer_create(CLOCK_REALTIME, &sev, &timerid) == -1) {
        perror("timer_create");
        exit(EXIT_FAILURE);
    }

    // 设置定时器的初始值和间隔值
    its.it_value.tv_sec = 1;
    its.it_value.tv_nsec = 0;
    its.it_interval.tv_sec = 1;
    its.it_interval.tv_nsec = 0; // 设置为0表示不重复

    // 开始定时器
    if (timer_settime(timerid, 0, &its, NULL) == -1) {
        perror("timer_settime");
        exit(EXIT_FAILURE);
    }

    // 主循环，等待定时器信号
    while (1) {
        pause(); // 等待信号
    }

    return 0;
}
