//gcc -o pw pw.c
#include <unistd.h>
#include <sys/types.h>
#include <pwd.h>
#include <stdio.h>

#define DEBUG_INFO(...) \
    do{\
        printf("%s:%d -- ", __func__, __LINE__);\
        printf(__VA_ARGS__); \
        printf("\n"); \
    }while(0)

int main()
{
    struct passwd *pw = getpwuid(getuid());
    printf("Username:%s\n",pw->pw_name);
    printf("Password:%s\n",pw->pw_passwd);
    printf("uid:%d\n",pw->pw_uid);
    printf("gid:%d\n",pw->pw_gid);
    printf("shell:%s\n",pw->pw_shell);
    printf("dir:%s\n",pw->pw_dir);
    
    do{
        pw = getpwent();
        if(!pw){
            perror("getpwent");
            break;
        }

        DEBUG_INFO("%s:%s:%d:%d:%s:%s:%s", 
        pw->pw_name,
        pw->pw_passwd,
        pw->pw_uid,
        pw->pw_gid,
        pw->pw_gecos,
        pw->pw_dir,
        pw->pw_shell);
    }while(1);
}
