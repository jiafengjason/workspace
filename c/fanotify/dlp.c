#define _ATFILE_SOURCE
#include <errno.h>
#include <inttypes.h>
#include <fcntl.h>
#include <linux/limits.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/select.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

#include <linux/fanotify.h>
#include <sys/fanotify.h>

#define FANOTIFY_ARGUMENTS "cdfhmnp"

int fan_fd;

static void usr1_handler(int sig __attribute__((unused)),
			 siginfo_t *si __attribute__((unused)),
			 void *unused __attribute__((unused)))
{
	fanotify_mark(fan_fd, FAN_MARK_FLUSH, 0, 0, NULL);
}

void decToBin(int num)
{
    if(num>0)
    {
        decToBin(num/2);
        printf("%d",num%2);
    }
}

int mark_object(int fan_fd, const char *path, int fd, uint64_t mask, unsigned int flags)
{
    printf("mask:%x\n", mask);
    printf("flags:%x\n", flags);
    printf("path:%s\n", path);
    return fanotify_mark(fan_fd, flags, mask, fd, path);
}

int set_special_ignored(int fan_fd, int fd, char *path)
{
	unsigned int flags = (FAN_MARK_ADD | FAN_MARK_IGNORED_MASK |
			      FAN_MARK_IGNORED_SURV_MODIFY);
	uint64_t mask = FAN_ALL_EVENTS | FAN_ALL_PERM_EVENTS;

	if (strcmp("/var/log/audit/audit.log", path) &&
	    strcmp("/var/log/messages", path) &&
	    strcmp("/var/log/wtmp", path) &&
	    strcmp("/var/run/utmp", path) &&
        strncmp("/usr/", path, 5) &&
        strncmp("/var/", path, 5) &&
        strncmp("/etc/", path, 5))
		return 0;

	return mark_object(fan_fd, NULL, fd, mask, flags);
}

int set_ignored_mask(int fan_fd, int fd, uint64_t mask)
{
	unsigned int flags = (FAN_MARK_ADD | FAN_MARK_IGNORED_MASK);

	return mark_object(fan_fd, NULL, fd, mask, flags);
}

int handle_perm(int fan_fd, struct fanotify_event_metadata *metadata, uint32_t response)
{
	struct fanotify_response response_struct;
	int ret;

	response_struct.fd = metadata->fd;
	response_struct.response = response;

    printf("Response:%d\n", response);
	ret = write(fan_fd, &response_struct, sizeof(response_struct));
	if (ret < 0)
		return ret;

	return 0;
}

void synopsis(const char *progname, int status)
{
	FILE *file = status ? stderr : stdout;

	fprintf(file, "USAGE: %s [-" FANOTIFY_ARGUMENTS "] "
		"[-o {open,close,access,modify,open_perm,access_perm}] "
		"file ...\n"
		"-c: learn about events on children of a directory (not decendants)\n"
		"-d: send events which happen to directories\n"
		"-f: set premptive ignores (go faster)\n"
		"-h: this help screen\n"
		"-m: place mark on the whole mount point, not just the inode\n"
		"-n: do not ignore repeated permission checks\n"
		"-p: check permissions, not just notification\n"
		"-s N: sleep N seconds before replying to perm events\n",
		progname);
	exit(status);
}

static char *get_program_name_from_pid(int pid, char *buffer, size_t buffer_size)
{
    int fd = 0;
    ssize_t len = 0;
    char *aux = NULL;
    
    // Try to get program name by PID
    sprintf (buffer, "/proc/%d/cmdline", pid);
    if ((fd = open (buffer, O_RDONLY)) < 0)
        return NULL;
    
    if ((len = read (fd, buffer, buffer_size - 1)) <= 0)
    {
        close (fd);
        return NULL;
    }
    close (fd);
    
    buffer[len] = '\0';
    aux = strstr (buffer, "^@");
    if (aux)
        *aux = '\0';
    
    return buffer;
}

int getFatherPid(int pid, char *dpath)
{
    char dir[1024]={0};
    char statPath[1024] = {0};
    char buf[1024] = {0};
    int fpid=0;
    char path[1024]={0};
    struct stat st;
    ssize_t ret =0;

    sprintf(dir,"/proc/%d/",pid);

    sprintf(statPath,"%sstat",dir);

    if(stat(statPath,&st)!=0)
    {
        return -2; 
    }

    memset(buf,0,strlen(buf));

    FILE * fp = fopen(statPath,"r");

    ret += fread(buf + ret,1,300-ret,fp);

    fclose(fp);

    sscanf(buf,"%*d %*c%s %*c %d %*s",path,&fpid);

    path[strlen(path)-1]='\0';
    strcpy(dpath,path);

    return fpid;
}

int main(int argc, char *argv[])
{
    int opt;
    uint64_t fan_mask = FAN_OPEN | FAN_CLOSE | FAN_ACCESS | FAN_MODIFY;
    unsigned int mark_flags = FAN_MARK_ADD, init_flags = 0;
    bool opt_child, opt_on_mount, opt_add_perms, opt_fast, opt_ignore_perm;
    int opt_sleep;
    ssize_t len;
    char buf[8192];
    fd_set rfds;
    struct sigaction sa;
    uint32_t response = FAN_ALLOW;
    int pid = 0;
    int fpid = 0;
    int gpid = 0;
    char path[PATH_MAX] = {0};
    char fpath[PATH_MAX] = {0};
    char gpath[PATH_MAX] = {0};

    sa.sa_flags = SA_SIGINFO | SA_RESTART;
    sigemptyset(&sa.sa_mask);
    sa.sa_sigaction = usr1_handler;
    if (sigaction(SIGUSR1, &sa, NULL) == -1)
        goto fail;

    opt_child = opt_on_mount = opt_add_perms = opt_fast = false;
    opt_ignore_perm = true;
    opt_sleep = 0;

    /* (0) 命令的参数解析 */
    while ((opt = getopt(argc, argv, "o:s:p:"FANOTIFY_ARGUMENTS)) != -1) {
        switch(opt) {
            case 'o': {
                char *str, *tok;

                fan_mask = 0;
                str = optarg;
                while ((tok = strtok(str, ",")) != NULL) {
                    str = NULL;
                    if (strcmp(tok, "open") == 0)
                    {
                        printf("FAN_OPEN\n");
                        fan_mask |= FAN_OPEN;
                    }
                    else if (strcmp(tok, "close") == 0)
                    {
                        printf("FAN_CLOSE\n");
                        fan_mask |= FAN_CLOSE;
                    }
                    else if (strcmp(tok, "access") == 0)
                    {
                        printf("FAN_ACCESS\n");
                        fan_mask |= FAN_ACCESS;
                    }
                    else if (strcmp(tok, "modify") == 0)
                    {
                        printf("FAN_MODIFY\n");
                        fan_mask |= FAN_MODIFY;
                    }
                    else if (strcmp(tok, "open_perm") == 0)
                    {
                        printf("FAN_OPEN_PERM\n");
                        fan_mask |= FAN_OPEN_PERM;
                    }
                    else if (strcmp(tok, "access_perm") == 0)
                    {
                        printf("FAN_ACCESS_PERM\n");
                        fan_mask |= FAN_ACCESS_PERM;
                    }
                    else
                        synopsis(argv[0], 1);
                }
                break;
            }
            case 'c':
                opt_child = true;
                break;
            case 'd':
                printf("FAN_ONDIR\n");
                fan_mask |= FAN_ONDIR;
                break;
            case 'f':
                opt_fast = true;
                opt_ignore_perm = true;
                break;
            case 'm':
                opt_on_mount = true;
                break;
            case 'n':
                opt_fast = false;
                opt_ignore_perm = false;
                break;
            case 'p':
                opt_add_perms = true;
                if (strcmp(optarg, "deny") == 0)
                {
                    printf("FAN_DENY\n");
                    response = FAN_DENY;
                }
                break;
            case 's':
                opt_sleep = atoi(optarg);
                break;
            case 'h':
                synopsis(argv[0], 0);
            default:  /* '?' */
                synopsis(argv[0], 1);
        }
    }

    if (optind == argc)
        synopsis(argv[0], 1);

    if (opt_child)
        fan_mask |= FAN_EVENT_ON_CHILD;

    if (opt_on_mount)
        mark_flags |= FAN_MARK_MOUNT;

    if (opt_add_perms)
        fan_mask |= FAN_ALL_PERM_EVENTS;

    if (fan_mask & FAN_ALL_PERM_EVENTS)
        init_flags |= FAN_CLASS_CONTENT;
    else
        init_flags |= FAN_CLASS_NOTIF;

    /* (1) 创建fanotify对应的文件句柄fd */
    fan_fd = fanotify_init(init_flags, O_RDONLY | O_LARGEFILE);
    printf("fanotify_init:%d\n", fan_fd);
    if (fan_fd < 0)
        goto fail;

    /* (2) 配置fd上需要监控的对象和操作类型 */
    for (; optind < argc; optind++)
        if (mark_object(fan_fd, argv[optind], AT_FDCWD, fan_mask, mark_flags) != 0)
            goto fail;

    FD_ZERO(&rfds);
    FD_SET(fan_fd, &rfds);

    while (select(fan_fd+1, &rfds, NULL, NULL, NULL) < 0)
    {
        if (errno != EINTR)
            goto fail;
    }

    printf("read\n");
    /* (3) 通过fd的read()操作来接收监控消息 */
    while ((len = read(fan_fd, buf, sizeof(buf))) > 0) {
        struct fanotify_event_metadata *metadata;
        char path[PATH_MAX];
        int path_len;

        /* (4) 逐个取出监控event消息并处理 */
        metadata = (void *)buf;
        while(FAN_EVENT_OK(metadata, len)) {
            //printf("Version:%d", metadata->vers);
            if (metadata->vers < 2) {
                fprintf(stderr, "Kernel fanotify version too old\n");
                goto fail;
            }

            /* (4.1) 忽略后续的重复消息 */
            if (metadata->fd >= 0 &&
                opt_fast &&
                set_ignored_mask(fan_fd, metadata->fd,
                         FAN_ALL_EVENTS | FAN_ALL_PERM_EVENTS))
                goto fail;

            if (metadata->fd >= 0) {
                sprintf(path, "/proc/self/fd/%d", metadata->fd);
                path_len = readlink(path, path, sizeof(path)-1);
                if (path_len < 0)
                    goto fail;
                path[path_len] = '\0';
                printf("%s:", path);
            } else
                printf("?:");

            /* (4.2) 对一些特殊目录，忽略重复消息 */
            set_special_ignored(fan_fd, metadata->fd, path);

            pid = metadata->pid;
            fpid = getFatherPid(pid, path);
            gpid = getFatherPid(fpid, fpath);
            getFatherPid(gpid, gpath);
            printf("path=%s pid=%d(%s) fpid=%ld(%s) gpid=%ld(%s)", path, pid, path, fpid, fpath, gpid, gpath);

            if (metadata->mask & FAN_ACCESS)
                printf(" access");
            if (metadata->mask & FAN_OPEN)
                printf(" open");
            if (metadata->mask & FAN_MODIFY)
                printf(" modify");
            if (metadata->mask & FAN_CLOSE) {
                if (metadata->mask & FAN_CLOSE_WRITE)
                    printf(" close(writable)");
                if (metadata->mask & FAN_CLOSE_NOWRITE)
                    printf(" close");
            }
            if (metadata->mask & FAN_OPEN_PERM)
                printf(" open_perm");
            if (metadata->mask & FAN_ACCESS_PERM)
                printf(" access_perm");

            printf("\n");
            
            /* (4.3) 权限允许消息的处理 */
            if (metadata->mask & FAN_ALL_PERM_EVENTS) {
                if (opt_sleep)
                    sleep(opt_sleep);

                if(strncmp(fpath, "firejail", strlen("firejail"))==0
                   || strncmp(gpath, "firejail", strlen("firejail"))==0
                   || strncmp(path, "fuse-overlayfs", strlen("fuse-overlayfs"))==0)
                {
                    response = FAN_ALLOW;
                }
                else
                {
                    response = FAN_DENY;
                }
                
                /* (4.3.1) fd的write()操作来发送允许的结果 */
                if (handle_perm(fan_fd, metadata, response))
                    goto fail;

                /* (4.3.2) 忽略后续的重复消息 */
                if (metadata->fd >= 0 &&
                    opt_ignore_perm &&
                    set_ignored_mask(fan_fd, metadata->fd,
                             metadata->mask))
                    goto fail;
            }
            
            fflush(stdout);

            /* (4.4) 关闭消息中的fd，并且取下一个消息 */
            if (metadata->fd >= 0 && close(metadata->fd) != 0)
                goto fail;
            metadata = FAN_EVENT_NEXT(metadata, len);
        }
        while (select(fan_fd+1, &rfds, NULL, NULL, NULL) < 0)
            if (errno != EINTR)
                goto fail;
    }
    if (len < 0)
        goto fail;
    return 0;

fail:
    fprintf(stderr, "%s\n", strerror(errno));
    return 1;
}
