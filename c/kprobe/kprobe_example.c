#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/kprobes.h>

static int pre_handler(struct kprobe *p, struct pt_regs *regs)
{
    printk(KERN_INFO "pre_handler: p->addr = 0x%p, ip = %lx, flags = 0x%lx\n", p->addr, regs->ip, regs->flags);
    return 0;
}

static void post_handler(struct kprobe *p, struct pt_regs *regs, unsigned long flags)
{
    printk(KERN_INFO "post_handler: p->addr = 0x%p, flags = 0x%lx\n", p->addr, regs->flags);
}

static int fault_handler(struct kprobe *p, struct pt_regs *regs, int trapnr)
{
    printk(KERN_INFO "fault_handler: p->addr = 0x%p, trap #%dn", p->addr, trapnr);
    return 0;
}

static struct kprobe kp = {
    .symbol_name   = "do_fork",      // 要追踪的内核函数为 do_fork
    .pre_handler   = pre_handler,    // pre_handler 回调函数
    .post_handler  = post_handler,   // post_handler 回调函数
    .fault_handler = fault_handler  // fault_handler 回调函数
};

static int __init kprobe_init(void)
{
    int ret;

    ret = register_kprobe(&kp); // 调用 register_kprobe 注册追踪点
    if (ret < 0) {
        printk(KERN_INFO "register_kprobe failed, returned %d\n", ret);
        return ret;
    }
    printk(KERN_INFO "planted kprobe at %p\n", kp.addr);
    return 0;
}

static void __exit kprobe_exit(void)
{
    unregister_kprobe(&kp); // 调用 unregister_kprobe 注销追踪点
    printk(KERN_INFO "kprobe at %p unregistered\n", kp.addr);
}

module_init(kprobe_init) // 注册模块初始化函数
module_exit(kprobe_exit) // 注册模块退出函数
MODULE_LICENSE("GPL");
