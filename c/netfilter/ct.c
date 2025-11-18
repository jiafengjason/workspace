//yum install libnetfilter_conntrack-devel
//gcc -o ct ct.c -lnetfilter_conntrack -lmnl
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <libmnl/libmnl.h>
#include <libnetfilter_conntrack/libnetfilter_conntrack.h>
#include <libnetfilter_conntrack/libnetfilter_conntrack_tcp.h>

/* 定义一个结构体来标识我们关心的上游连接 */
typedef struct {
    uint32_t src_ip;    // 网关SNAT后的IP（即本机出口IP）
    uint32_t dst_ip;    // 上游服务器IP（如Baidu的IP）
    uint16_t dst_port;  // 上游服务器端口（如80, 443）
} upstream_conn_key_t;

static int event_callback(const struct nlmsghdr *nlh, void *data)
{
    struct nf_conntrack *ct;
    int event_type;

    // 获取Netlink消息的类型
    event_type = nlh->nlmsg_type;
    printf("receive msg: type=0x%x, len=%d\n", nlh->nlmsg_type, nlh->nlmsg_len);

    ct = nfct_new();
    if (ct == NULL) return MNL_CB_OK;

    // 解析消息到conntrack结构体
    nfct_nlmsg_parse(nlh, ct);
    uint8_t state = nfct_get_attr_u8(ct, ATTR_TCP_STATE);
    uint32_t dst_ip = nfct_get_attr_u32(ct, ATTR_ORIG_IPV4_DST);
    uint16_t dst_port = nfct_get_attr_u16(ct, ATTR_ORIG_PORT_DST);
    uint8_t protonum = nfct_get_attr_u8(ct, ATTR_ORIG_L4PROTO);
    struct in_addr dip = { .s_addr = dst_ip };

    // 根据事件类型处理
    switch (event_type) {
        case (NFNL_SUBSYS_CTNETLINK << 8 | IPCTNL_MSG_CT_NEW):
            // 可能是新建，也可能是更新（状态变更）
            /*
            enum tcp_state {
                    TCP_CONNTRACK_NONE,
                    TCP_CONNTRACK_SYN_SENT,
                    TCP_CONNTRACK_SYN_RECV,
                    TCP_CONNTRACK_ESTABLISHED,
                    TCP_CONNTRACK_FIN_WAIT,
                    TCP_CONNTRACK_CLOSE_WAIT,
                    TCP_CONNTRACK_LAST_ACK,
                    TCP_CONNTRACK_TIME_WAIT,
                    TCP_CONNTRACK_CLOSE,
                    TCP_CONNTRACK_LISTEN,
            #define TCP_CONNTRACK_SYN_SENT2         TCP_CONNTRACK_LISTEN
                    TCP_CONNTRACK_MAX,
                    TCP_CONNTRACK_IGNORE
            };
            */
            switch (state) {
                case TCP_CONNTRACK_ESTABLISHED:
                    printf("EVENT: Connection to upstream %s:%u is ESTABLISHED: %d\n", inet_ntoa(dip), ntohs(dst_port), state);
                    // 触发您的处理逻辑：连接正在关闭/已关闭
                    break;
                case TCP_CONNTRACK_CLOSE:
                case TCP_CONNTRACK_CLOSE_WAIT:
                case TCP_CONNTRACK_TIME_WAIT:
                    printf("EVENT: Connection to upstream %s:%u is CLOSED: %d\n", inet_ntoa(dip), ntohs(dst_port), state);
                    // 触发您的处理逻辑：连接正在关闭/已关闭
                    break;
                default:
                    // 其他状态（SYN_SENT, SYN_RECV等），根据需要处理
                    break;
            }
            break;
        case (NFNL_SUBSYS_CTNETLINK << 8 | IPCTNL_MSG_CT_DELETE):
            printf("EVENT: Connection to upstream %s:%u is DELETED: %d\n", inet_ntoa(dip), ntohs(dst_port), state);
            // 触发您的处理逻辑：连接已彻底消失
            break;
        default:
            break;
    }

    nfct_destroy(ct);
    return MNL_CB_OK;
}

int main()
{
    struct mnl_socket *nl;
    char buf[MNL_SOCKET_BUFFER_SIZE];
    int ret;

    nl = mnl_socket_open(NETLINK_NETFILTER);
    if (nl == NULL) {
        perror("mnl_socket_open");
        exit(EXIT_FAILURE);
    }

    // 绑定Socket，并加入连接跟踪事件组
    // NFNLGRP_CONNTRACK_NEW: 监听新建连接事件
    // NFNLGRP_CONNTRACK_UPDATE: 监听更新事件（如状态变更）
    // NFNLGRP_CONNTRACK_DESTROY: 监听销毁/删除事件
    //int grp_id = NFNLGRP_CONNTRACK_NEW | NFNLGRP_CONNTRACK_UPDATE | NFNLGRP_CONNTRACK_DESTROY;
    unsigned int grp_id = (1 << (NFNLGRP_CONNTRACK_NEW - 1)) |
                          (1 << (NFNLGRP_CONNTRACK_UPDATE - 1)) |
                          (1 << (NFNLGRP_CONNTRACK_DESTROY - 1));

    if (mnl_socket_bind(nl, grp_id, MNL_SOCKET_AUTOPID) < 0) {
        perror("mnl_socket_bind");
        mnl_socket_close(nl);
        exit(EXIT_FAILURE);
    }

    printf("Listening for conntrack events...\n");
    while (1) {
        // 阻塞等待，直到内核发送事件通知
        ret = mnl_socket_recvfrom(nl, buf, sizeof(buf));
        if (ret == -1) {
            perror("mnl_socket_recvfrom");
            continue;
        }

        // 处理收到的消息，调用回调函数
        ret = mnl_cb_run(buf, ret, 0, 0, event_callback, NULL);
        if (ret <= MNL_CB_STOP) {
            break;
        }
    }
    mnl_socket_close(nl);
    return 0;
}