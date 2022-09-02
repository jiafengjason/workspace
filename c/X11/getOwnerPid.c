//apt-get install libx11-dev
//gcc -o getOwnerPid getOwnerPid.c `pkg-config glib-2.0 --libs --cflags` -lX11 -Wall
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

    if (!XQueryTree(display, win, &root, &parent, &children, &nchildren))
        return None;

    printf("win:%#lx root:%#lx parent:%#lx\n", win, root, parent);

    if (children) XFree((char *)children);

    return parent;
}

int main(int argc, char **argv)
{
    Display *display = XOpenDisplay(NULL);       //获取默认的display指针
    Window win;
    Atom xa_prop_name;
    Atom xa_ret_type;
    Atom property;
    int ret_format;
    unsigned long ret_nitems;
    unsigned long ret_bytes_after;
    unsigned char *ret_prop;
    int pid;
    int size;

    Atom CLIPBOARD = XInternAtom(display, "CLIPBOARD", False);
    win = XGetSelectionOwner(display, XA_PRIMARY);
    printf("xwindow id: 0x%0lx\n", win);
    win = XGetSelectionOwner(display, CLIPBOARD);
    printf("xwindow id: 0x%0lx\n", win);

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
        printf("xa_ret_type=%ld ret_format=%d ret_nitems=%ld\n", xa_ret_type, ret_format, ret_nitems);
        if(xa_ret_type) {
            size = ret_format*ret_nitems/8;
            memcpy(&pid, ret_prop, size);// 类型传换
            printf("window pid: %d\n", pid);
        }
        getParentWindow(display, win);
    }
    
    property = XInternAtom(display, "_QT_SELECTION", False);
    if (XGetWindowProperty (display, win,
            property, 0L, 1000000,
            False, (Atom)AnyPropertyType, &xa_ret_type,         // XA_CARDINAL为数值类型
                                &ret_format, &ret_nitems, &ret_bytes_after,
                                &ret_prop) != Success)       // 后五个参数是返回值
    {
        printf("Cannot get %s property.\n", "_QT_SELECTION");
    }
    else
    {
        printf("xa_ret_type=%ld ret_format=%d ret_nitems=%ld ret_prop=%s\n", xa_ret_type, ret_format, ret_nitems, ret_prop);
    }
}
