//export LIBRARY_PATH=$LIBRARY_PATH:/home/enlink/lib
//gcc main.c -g -L. -lpthread -lhiredis -I. `pkg-config --cflags --libs libevent.pc` -o main
//gcc main.c -g -L. -lpthread -lhiredis -I. -I/usr/local/include  -L/usr/local/lib -levent -o main

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

#include <adapters/libevent.h>
#include <event2/event.h>

#include <redis_hiredis.h>
#include <redis_async.h>

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
    redisAsyncContext *redis_actx = NULL;
    struct event_base *base = NULL;

    if(redis_actx != NULL){
        printf("redis_actx not NULL\n");
        return NULL;
    }

    base = event_base_new();//�½�һ��libevent�¼�����

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
    redisLibeventAttach(redis_actx,base);//��������ӵ�libevent�¼�����
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
    
    event_base_dispatch(base);//��ʼlibeventѭ����ע������һ��֮ǰredis�ǲ���������ӵģ�ǰ�ߵ��õ�����ͺ���Ҳû��������������
    
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
