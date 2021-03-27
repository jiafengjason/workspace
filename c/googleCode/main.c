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
#include <libmnl/libmnl.h>
#include <linux/netfilter.h>
#include <linux/netfilter/nfnetlink.h>

#include <linux/types.h>
#include <linux/netfilter/nfnetlink_queue.h>

#include <libnetfilter_queue/libnetfilter_queue.h>

/* only for NFQA_CT, not needed otherwise: */
#include <linux/netfilter/nfnetlink_conntrack.h>
#include <redis_hiredis.h>
#include "json_object.h"
#include "json_tokener.h"

//获取6位校验码
static int generateCode(const char *key) 
{
    int i;
    printf("key:%p\n",key);
    printf("strlen:%d\n",strlen(key));
    for(i=0;i<strlen(key);i++){
    
        printf("%c",key[i]);
    
    }
    printf("\n");

    return 1;
}

static int checkCode(int userid) 
{
    char secret[100] = "HEYTAMBQGAYDAMBR";
    int i=0;

    printf("secret:%p\n",secret);
    printf("strlen:%d\n",strlen(secret));
    for(i=0;i<strlen(secret);i++){
    
        printf("%c",secret[i]);
    
    }
    printf("\n");

    generateCode(secret);
    return NF_ACCEPT;
}

int getCmdFilterRules()
{
    char hostname[] = "127.0.0.1";
    int port = 6379;
    redisContext *redis_ctx;
    redisReply *reply;
    struct timeval tv;
    json_object* all_json = NULL;
    json_object* key_json = NULL;
    json_object* item = NULL;
    int i=0;
    
    redis_ctx  = redisConnect("127.0.0.1", 6379);
    if (redis_ctx == NULL || redis_ctx->err)
    {
        if (redis_ctx) 
        {
            printf("Connection error: %s\n", redis_ctx->errstr);
            redisFree(redis_ctx);
        }
        else
        {
            printf("Connection error: can't allocate redis context\n");
        }
        return -1;
    }
    
    
    tv.tv_sec = 1;
    redisSetTimeout(redis_ctx ,tv);

    reply = redisCommand(redis_ctx, "AUTH enlink");
    if(reply==NULL)
    {
        printf("Auth failed 1!\n");
        return -1;
    }
    freeReplyObject(reply);

    //reply = redisCommand(redis_ctx, "HMSET enlink:gate:cmd:rules test rm");
    //freeReplyObject(reply);

    reply = redisCommand(redis_ctx, "HGET enlink:gate:http:global terminallist");
    if(reply==NULL)
    {
        printf("HGET enlink:gate:http:global terminallist failed!\n");
        return -1;
    }
    
    all_json = json_tokener_parse(reply->str);
    if(all_json  == NULL){
        return -1;
    }
    
    for(i=0; i < json_object_array_length(all_json); i++) {
        item = json_object_array_get_idx(all_json, i);
        printf("\t[%d]=%d\n", i, json_object_get_int(item));
    }

    json_object_put(all_json);
    freeReplyObject(reply);
    redisFree(redis_ctx);
    return 0;
}

bool matchReg(char *pattern, char *buf, size_t nmatch, regmatch_t *pmatch)
{
    int status;
    regex_t reg;
    
    //编译正则模式
    status = regcomp(&reg,pattern,REG_EXTENDED);
    if(status)
    {
        return false;
    }
    //执行正则表达式和缓存的比较
    status = regexec(&reg,buf,nmatch,pmatch,0);
    regfree(&reg);
    
    if(status==0)
    {
        return true;
    }
    
    return false;
}

int main(int argc, char *argv[]) 
{
    /*
    char haystack[] = "l";
    char needle[] = "\r\n";
    char *ret = NULL;
    
    ret = strstr(haystack, needle);
    if(ret)
    {
        printf("Not null");
    }
    printf("%p\n", ret);
    
    
    char pattern[100] = "^rm+";
    regmatch_t pmatch[1];
    const size_t nmatch=1;
    bool match = false;

    match = matchReg(pattern, "rm -rf a", nmatch, pmatch);
    printf("%d\n", match);
    */
    getCmdFilterRules();
}
