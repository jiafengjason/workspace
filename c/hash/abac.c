//gcc -o uuid uuid.c -luuid

#include <uuid/uuid.h>
#include <stdio.h>
#include <sys/socket.h>
#include <openssl/ssl.h>
#include "hash.h"
#include "list.h"

typedef struct gated_node_abac_s
{
    struct list_head    node;
    int                 fd;
    struct sockaddr     dst;
    char                uuid[40];
    SSL_CTX             *ctx;
    SSL                 *ssl;
}gated_node_abac_t;

int main(int argc, char **argv)
{
    uuid_t binuuid;
    hash_t              *h;
    gated_node_abac_t *node = NULL;
    int ret = 0;

    h = hash_create(100000, NULL, NULL);
    
    while(1) {
        node = calloc(1, sizeof(*node));
        if (!node) {
            return -1;
        }
        
        uuid_generate(binuuid);
        uuid_unparse(binuuid, node->uuid);
        printf("%s\n", node->uuid);
        
        ret = hash_alloc_insert(h, node->uuid, node);
        if(ret==0) {
            free(node);
            return -1;
        }
        
        hnode_t *hn = hash_lookup(h, node->uuid);
        if (hn) {
            printf("[Abac]hash_scan_delfree uuid:%s hn:%p node:%p\n", node->uuid, hn, node);
            hash_scan_delfree(h, hn);
        }
    }
    return 0;
}
