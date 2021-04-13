//export LIBRARY_PATH=$LIBRARY_PATH:/home/enlink/lib
//gcc epoll.c -g -L. -lpthread -lhiredis -I. -o epoll

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <time.h>
#include <assert.h>
#include <dlfcn.h>
#include <fcntl.h>
#include <getopt.h>
#include <pwd.h>
#include <regex.h>
#include <arpa/inet.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <pthread.h>
#include <sys/epoll.h>

#include <redis_hiredis.h>
#include <redis_async.h>

#define EPOLLEVENTS 1

void* redis_subscribe_terminal_thread(void *data);

void redis_async_disconnect_cb(const struct redisAsyncContext *redis_actx, int status){
    if(status != REDIS_OK)
    {
        printf("Disconnect error: %s\n", redis_actx->errstr);
        redis_subscribe_terminal_thread(NULL);
        return;
    }
    printf("Redis async disconnect\n");
}

void redis_async_connect_cb(const struct redisAsyncContext *redis_actx, int status){
    if(status != REDIS_OK)
    {
        printf("Connect error: %s\n", redis_actx->errstr);
        return;
    }
    printf("Redis async connect!\n");
}

void redis_terminal_event(struct redisAsyncContext *redis_actx, void* r, void* privdata)
{
    printf("redis_terminal_event!\n");
}

void* redis_subscribe_terminal_thread(void *data)
{
    int ret = 0;
    int i;
    int s;
    int efd;
    struct epoll_event event;
    struct epoll_event events[EPOLLEVENTS];
    redisAsyncContext *redis_actx = NULL;
    struct event_base *base = NULL;

    if(redis_actx != NULL){
        printf("redis_actx not NULL\n");
        return NULL;
    }

    //base = event_base_new();//�½�һ��libevent�¼�����

    redis_actx = redisAsyncConnect("127.0.0.1", 6379);
    if(redis_actx == NULL){
        printf("RedisAsyncConnect fail!\n");
        return NULL;
    }

    if (redis_actx->err) {
        printf("RedisAsyncConnect error: %s\n", redis_actx->err);
        return NULL;
    }

    //���ûص�����
    //redis_actx->data = user;
    //redisLibeventAttach(redis_actx,base);//��������ӵ�libevent�¼�����
    redisAsyncSetDisconnectCallback(redis_actx, redis_async_disconnect_cb);
    redisAsyncSetConnectCallback(redis_actx, redis_async_connect_cb);

    ret = redisAsyncCommand(redis_actx,NULL,NULL,"AUTH enlink");
    if(ret < 0){
        printf("AUTH fail!\n");
        return NULL;
    }

    /*���ļ��ռ�֪ͨ,��עredis session��������*/
    ret = redisAsyncCommand(redis_actx,NULL,NULL,"config set notify-keyspace-events KA");
    if(ret < 0){
        printf("config set notify-keyspace-events KA fail!\n");
        return NULL;
    }

    /*����session id key�仯�¼�*/ 
    ret = redisAsyncCommand(redis_actx,redis_terminal_event,NULL,"psubscribe __keyspace@0__:enlink:gate:http:terminal");
    if(ret < 0){
        printf("psubscribe __keyspace@0__:enlink:gate:http:terminal fail!\n");
        return NULL;
    }
    
    efd = epoll_create(1);
    if (efd == -1)
    {
        printf("Epoll create error!\n");
        return NULL;
    }
    
    event.data.fd = redis_actx->c.fd;
    event.events = EPOLLIN | EPOLLET | EPOLLOUT;
    s = epoll_ctl (efd, EPOLL_CTL_ADD, redis_actx->c.fd, &event);
    if (s == -1)
    {
        printf ("Epoll ctl error!\n");
        return NULL;
    }
    printf("epoll_wait!\n");
    while (1)
    {
        ret = epoll_wait(efd,events,EPOLLEVENTS,-1);
        
        for (i = 0;i < EPOLLEVENTS;i++)
        {
            if(events[i].data.fd == redis_actx->c.fd)
            {
                //���������������ͺ��¼����ͽ��д���
                if (events[i].events & EPOLLIN)
                {
                    printf("redisAsyncHandleRead!\n");
                    redisAsyncHandleRead(redis_actx);
                }
                else if(events[i].events & EPOLLOUT)
                {
                    printf("redisAsyncHandleWrite!\n");
                    redisAsyncHandleWrite(redis_actx);
                }
            }
        }
    }
    //event_base_dispatch(base);//��ʼlibeventѭ����ע������һ��֮ǰredis�ǲ���������ӵģ�ǰ�ߵ��õ�����ͺ���Ҳû��������������
    
    return NULL;
}

int main(int argc, char *argv[]) 
{
    /*
    pthread_t subscribe_thread;
    
    if (pthread_create(&(subscribe_thread), NULL, redis_subscribe_terminal_thread, NULL))
    {
        printf("Unable to start subscribe thread");
    }
    */
    redis_subscribe_terminal_thread(NULL);
}
