#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <syscall.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
 
#if __WORDSIZE == 64
#define REG(reg) reg.orig_rax
#else
#define REG(reg) reg.orig_eax
#endif
 
int main(int argc, char* argv[]) { 
    pid_t child;
    child = fork();
    if(child == 0) {
        ptrace(PTRACE_TRACEME, 0, NULL, NULL);
        execl("/home/workspace/c/ptrace/a.out", "a.out", NULL);
    } else {
        int status;
        while(waitpid(child, &status, 0) && ! WIFEXITED(status)) {
            struct user_regs_struct regs;
            ptrace(PTRACE_GETREGS, child, NULL, &regs);
            if (REG(regs) == 87) {
                fprintf(stderr, "error: call syscall unlink() is not allowed!\n");
                kill(child, SIGKILL);
                return 0;
            }
            fprintf(stdout, "Process executed systemcallID: [%ld]\n", REG(regs));
            ptrace(PTRACE_SYSCALL, child, NULL, NULL);
        }
    }
    exit(0);
}
