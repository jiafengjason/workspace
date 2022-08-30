//apt-get install libx11-dev
//gcc -o getOwnerPid getOwnerPid.c `pkg-config glib-2.0 --libs --cflags` -lX11 -Wall
#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <stdio.h>
#include <string.h>
 
#define MAX_PROPERTY_VALUE_LEN 4096    //取得属性值最大长度
 
int main(int argc, char **argv)
{
	Display *disp = XOpenDisplay(NULL);       //获取默认的display指针
	Window win;
	Atom xa_prop_name;
	Atom xa_ret_type;
	int ret_format;
	unsigned long ret_nitems;
	unsigned long ret_bytes_after;
	unsigned char *ret_prop;
	int id;

	Atom CLIPBOARD = XInternAtom(disp, "CLIPBOARD", False);
	win = XGetSelectionOwner(disp, CLIPBOARD);

	printf("xwindow id: 0x%0x\n", win);

	xa_prop_name = XInternAtom(disp, "_NET_WM_PID", False);  // 取对应字串的AtomID

	if (XGetWindowProperty(disp, win, xa_prop_name, 0,           // 获取窗口属性
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
		memcpy(&id, ret_prop, 4);// 类型传换
		printf("window pid: %d\n", id);
	}
}
