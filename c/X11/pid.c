//gcc -o pid pid.c `pkg-config glib-2.0 --libs --cflags` -lX11 -Wall
#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <stdio.h>
#include <string.h>
 
#define MAX_PROPERTY_VALUE_LEN 4096    //取得属性值最大长度
 
int main(int argc, char **argv)
{
        Display *disp = XOpenDisplay(NULL);       //获取默认的display指针
        Window win = NULL;
        int ret = -1;
        Atom xa_prop_name;
        Atom xa_ret_type;
        int ret_format;
        unsigned long ret_nitems;
        unsigned long ret_bytes_after;
        unsigned long tmp_size;
        unsigned char *ret_prop;
        int id;
 
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
 
        printf("xwindow id: 0x%0x\n", win);
 
        xa_prop_name = XInternAtom(disp, "_NET_WM_PID", False);  // 取对应字串的AtomID
 
        if (XGetWindowProperty(disp, win, xa_prop_name, 0,           // 获取窗口属性
                                    MAX_PROPERTY_VALUE_LEN / 4,
                                    False, XA_CARDINAL, &xa_ret_type,         // XA_CARDINAL为数值类型
                                    &ret_format, &ret_nitems, &ret_bytes_after,
                                    &ret_prop) != Success)       // 后五个参数是返回值
        {
                 printf("Cannot get %s property.\n", "_NET_WM_PID");
                 return NULL;
        }
        else
        {
                 memcpy(&id, ret_prop, 4);// 类型传换
                 printf("window pid: %d\n", id);
        }
}
