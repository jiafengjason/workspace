//apt-get install libx11-dev
//gcc -o pid pid.c `pkg-config glib-2.0 --libs --cflags` -lX11 -Wall
#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <stdio.h>
#include <string.h>
 
#define MAX_PROPERTY_VALUE_LEN 4096    //取得属性值最大长度

Window getParentWindow(Display *display, Window win)
{
    Window root, parent;
    Window *children;
    unsigned int nchildren;
    int i;

    if (!XQueryTree(display, win, &root, &parent, &children, &nchildren))
        return None;

    printf("nchildren:%d\n", nchildren);
    for (i=0; i<nchildren; i++)
    {
        printf("child:%#lx\n", children[i]);
    }

    printf("win:%#lx root:%#lx parent:%#lx\n", win, root, parent);

    if (children) XFree((char *)children);

    return parent;
}

int main(int argc, char **argv)
{
    Display *display = XOpenDisplay(NULL);       //获取默认的display指针
    Window win;
    int ret = -1;
    Atom xa_prop_name;
    Atom xa_ret_type;
    int ret_format;
    unsigned long ret_nitems;
    unsigned long ret_bytes_after;
    unsigned char *ret_prop;
    int pid;
    int size;

    if (argc < 2)
    {
         printf("please input windowID, such as: ./main 0x240001e (use command xwininfo)\n");
         return -1;
    }

    ret = sscanf(argv[1], "0x%0x", &win);         // 从程序参数中获取xwindow id
    if (ret < 1)
    {
         printf("please input windowID, such as: ./main 0x240001e (use command xwininfo)\n");
         return -1;
    }

    printf("xwindow id: %#lx\n", win);

    xa_prop_name = XInternAtom(display, "_NET_WM_PID", False);  // 取对应字串的AtomID

    if (XGetWindowProperty(display, win, xa_prop_name, 0,           // 获取窗口属性
                                MAX_PROPERTY_VALUE_LEN / 4,
                                False, XA_CARDINAL, &xa_ret_type,         // XA_CARDINAL为数值类型
                                &ret_format, &ret_nitems, &ret_bytes_after,
                                &ret_prop) != Success)       // 后五个参数是返回值
    {
         printf("Cannot get %s property.\n", "_NET_WM_PID");
    }
    else
    {
        if(xa_ret_type) {
            size = ret_format*ret_nitems/8;
            memcpy(&pid, ret_prop, size);// 类型传换
            printf("window pid: %d\n", pid);
        }
        getParentWindow(display, win);
    }
}
