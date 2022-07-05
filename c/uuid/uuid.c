//gcc -o uuid uuid.c -luuid

#include <uuid/uuid.h>
#include <stdio.h>

int main(int argc, char **argv)
{
    uuid_t binuuid;
    char uuid[37];
 
    uuid_generate(binuuid);
    uuid_unparse(binuuid, uuid);
    printf("%s\n", uuid);

    uuid_unparse_upper(binuuid, uuid);
    printf("%s\n", uuid);

    uuid_unparse_lower(binuuid, uuid);
    printf("%s\n", uuid);

    return 0;
}
