// gcc -fPIC -shared -o libadd.so add.c
// gcc -o openSo openSo.c -ldl; ./openSo
// output: 1 add 2 is 3

#include <stdio.h>  
#include <stdlib.h>   // EXIT_FAILURE
#include <dlfcn.h>    // dlopen, dlerror, dlsym, dlclose

typedef int(* FUNC_ADD)(int, int); // ���庯��ָ�����͵ı���
//const char* dllPath = "./libadd.so";
const char* dllPath = "libguac-client-ssh.so";

int main()
{
    void* handle = dlopen( dllPath, RTLD_LAZY );

    if( !handle )
    {
        fprintf( stderr, "[%s](%d) dlopen get error: %s\n", __FILE__, __LINE__, dlerror() );
        exit( EXIT_FAILURE );
    }
    printf("Hello World");
    /*
    do{ // for resource handle
        FUNC_ADD add_func = (FUNC_ADD)dlsym( handle, "add" );
        printf( "1 add 2 is %d \n", add_func(1,2) );
    }while(0); // for resource handle
    dlclose( handle );
    */
}