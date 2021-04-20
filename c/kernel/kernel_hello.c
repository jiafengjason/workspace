//yum -y install kernel-headers
//yum -y install kernel-devel
//gcc hello.c -o hello
#include <linux/init.h>         // module_init module_exit 宏定义
#include <linux/module.h>       // MODULE_LICENSE MODULE_AUTHOR MODULE_DESCRIPTION MODULE_VERSION

/* 以下4个宏分别是许可证，作者，模块描述，模块版本 */
MODULE_LICENSE("Dual BSD/GPL");
MODULE_AUTHOR("calling love");
MODULE_DESCRIPTION("hello kernel programming");
MODULE_VERSION("1.0");

int hello_init(void)
{
    printk(KERN_ALERT "Hello World!\n");// 内核日志输出,KERN_ALERT表示日志的级别,是个字符串
    return 0;
}

void hello_cleanup(void)
{
    printk(KERN_ALERT "Goodbye!\n");
}

/* 注册到内核 */
module_init(hello_init);
module_exit(hello_cleanup);