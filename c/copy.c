//gcc -o copy copy.c
#include <unistd.h>
#include <sys/types.h>
#include <pwd.h>
#include <stdio.h>

int copy_file(char *src, char *dst) {
    FILE *rfp = NULL; // 指向要复制的文件
    FILE *wfp = NULL; // 指向复制后的文件
    int len = 1024*4; // 缓冲区长度
    char buffer[4*1024];
    int cnt; // 实际读取的字节数
    if( (rfp=fopen(src, "rb")) == NULL || (wfp=fopen(dst, "wb")) == NULL ){
        if(rfp) {
            fclose(rfp);
        }
        if(wfp) {
            fclose(wfp);
        }
        return 0;
    }
    // 不断从fileRead读取内容，放在缓冲区，再将缓冲区的内容写入fileWrite
    while( (cnt=fread(buffer, 1, len, rfp)) > 0 ){
        fwrite(buffer, cnt, 1, wfp);
    }
    fclose(rfp);
    fclose(wfp);
    return 1;
}

int main()
{
    copy_file("/home/record.go", "/root/record.go");
}
