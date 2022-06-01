#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include<arpa/inet.h>

#define ngx_str3_cmp(m, c0, c1, c2, c3)                                       \
    *(uint32_t *) m == ((c3 << 24) | (c2 << 16) | (c1 << 8) | c0)

#define ngx_str4cmp(m, c0, c1, c2, c3)                                        \
    *(uint32_t *) m == ((c3 << 24) | (c2 << 16) | (c1 << 8) | c0)


typedef struct gated_acl_s {
    char af_type;
    char proto;
    union {
    	int		all[4];
    	int		ip;
    	int		ip6[4];
    	struct in_addr	in;
    	struct in6_addr	in6;
    }ip_start;

    union {
    	int		all[4];
    	int		ip;
    	int		ip6[4];
    	struct in_addr	in;
    	struct in6_addr	in6;
    }ip_end;

    unsigned short minport;
    unsigned short maxport;
    unsigned short code;
}gated_acl_t;

static int parse_acl_rule(gated_acl_t *rule, char *buf)
{
    u_char  c, ch, *p, *m;

    enum {
        sw_start = 0,
        sw_aftype,
        sw_protocol_start,
        sw_protocol,
        sw_ip1_start,
        sw_ip1,
        sw_ip2_start,
        sw_ip2,
        sw_port_start,
        sw_port,
        sw_port_range_start,
        sw_port_range,
        sw_port_any,
        sw_code_start,
        sw_code,
        sw_almost_done
    } state;

    state = sw_start;
    
    for (p = buf; *p != '\0'; p++) {
        ch = *p;

        switch (state) {
        case sw_start:
            if (ch != 'I') {
                return -1;
            }
            m = p;
            state = sw_aftype;
            break;

        case sw_aftype:
            if (ch == '|') {
                if ((p - m) != 4) {
                    return -1;
                }
                if (ngx_str4cmp(m, 'I', 'P', 'v', '4')) {
                    rule->af_type = AF_INET;
                } else if (ngx_str4cmp(m, 'I', 'P', 'v', '6')) {
                    rule->af_type = AF_INET6;
                } else {
                    return -1;
                }
                state = sw_protocol_start;
                break;
            }
            break;
        case sw_protocol_start:
            if (ch == '|')
                return -1;
            m = p;
            state = sw_protocol;
            break;
        case sw_protocol:
            if (ch == '|') {
                if ((p - m) != 3) {
                    return -1;
                }
                if (ngx_str3_cmp(m, 'T', 'C', 'P', '|')) {
                    rule->proto = 6;
                } else if (ngx_str3_cmp(m, 'U', 'D', 'P', '|')) {
                    rule->proto = 17;
                } else if (ngx_str3_cmp(m, 'A', 'N', 'Y', '|')) {
                    rule->proto = 0;
                } else {
                    return -1;
                }
                state = sw_ip1_start;
                break;
            }
            break;
        case sw_ip1_start:
            if (ch == '|')
                return -1;
            m = p;
            state = sw_ip1;
            break;
        case sw_ip1:
            if (ch == '-') {
                *p = '\0';
                if (0 == inet_pton(rule->af_type, m, &rule->ip_start)) {
                    *p = '-';
                    return -1;
                }
                *p = '-';
                state = sw_ip2_start;
            } else if (ch == '|') {
                *p = '\0';
                if (0 == inet_pton(rule->af_type, m, &rule->ip_start)) {
                    *p = '-';
                    return -1;
                }
                *p = '|';
                memcpy(&rule->ip_end, &rule->ip_start, sizeof(rule->ip_start));
                state = sw_port_start;
            }
            break;
        case sw_ip2_start:
            if (ch == '|')
                return -1;
            m = p;
            state = sw_ip2;
            break;
        case sw_ip2:
            if (ch == '|') {
                *p = '\0';
                if (0 == inet_pton(rule->af_type, m, &rule->ip_end)) {
                    *p = '-';
                    return -1;
                }
                *p = '|';
                state = sw_port_start;
            }
            break;
        case sw_port_start:
            m = p;
            if (ch == 'A') {
                state = sw_port_any;
            } else {
                state = sw_port;
            }
            break;
        case sw_port_any:
            if (ch == '|') {
                if( 0 == strncmp(m, "ANY", 3)) {
                    rule->minport = 1;
                    rule->maxport = 65535;
                } else {
                    return -1;
                }
                state = sw_code_start;
            }
            break;
        case sw_port:
            if (ch == '-') {
                *p = '\0';
                rule->minport = atoi(m);
                *p = '-';
                state = sw_port_range_start;
                break;
            } else if (ch == '|') {
                rule->minport = rule->maxport = atoi(m);
                if (rule->minport < 1 || rule->maxport > 65535) {
                    return -1;
                }
                state = sw_code_start;
            }

            break;
        case sw_port_range_start:
            if (ch < '0' || ch > '9') {
                return -1;
            }
            m = p;
            state = sw_port_range;
            break;
        case sw_port_range:
            if (ch == '|') {
                rule->maxport = atoi(m);
                if (rule->minport < 1 || rule->maxport > 65535 || rule->minport > rule->maxport) {
                    return -1;
                }
                state = sw_code_start;
            } else if (ch < '0' || ch > '9') {
                return -1;
            }
            break;
        case sw_code_start:
            if (ch < '0' || ch > '9') {
                return -1;
            }
            m = p;
            state = sw_code;
            break;
        case sw_code:
            break;
        }
    }
    
    if (state != sw_port && state != sw_port_any && state != sw_port_range && state != sw_code) {
        return -1;
    }
    if (state == sw_port_any) {
        if(0 == strncmp(m, "ANY", 3)) {
            rule->minport = 1;
            rule->maxport = 65535;
        } else {
            return -1;
        }
    } else if (state == sw_port) {
        rule->minport = rule->maxport = atoi(m);
        if (rule->minport < 1 || rule->maxport > 65535) {
            return -1;
        }
    } else if (state == sw_port_range) {
        rule->maxport = atoi(m);
        if (rule->minport < 1 || rule->maxport > 65535 || rule->minport > rule->maxport) {
            return -1;
        }
    } else if (state == sw_code) {
        rule->code = atoi(m);
    }
    return 0;
}

void print_acl(gated_acl_t *prule)
{
    char str[128];
    printf("af_type = %d\n", prule->af_type);
    printf("proto = %d\n", prule->proto);
    printf("begin ip = %s\n", inet_ntop(prule->af_type, &prule->ip_start, str, 128));
    printf("end ip = %s\n", inet_ntop(prule->af_type, &prule->ip_end, str, 128));
    printf("min port = %d\n", prule->minport);
    printf("max prot = %d\n", prule->maxport);
    printf("code = %d\n", prule->code);
}

int main(void)
{
    gated_acl_t rule;
    int ret = 0;
    char aclStr[100] = "IPv4|TCP|100.1.1.0-100.1.1.3|ANY|2";

    ret = parse_acl_rule(&rule, aclStr);
    printf("ret:%d\n", ret);
    print_acl(&rule);
}
