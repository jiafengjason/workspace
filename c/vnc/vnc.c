//apt install libvncserver-dev libx11-dev libxfixes-dev libxtst-dev
//g++ -lvncserver -lX11 -lXfixes -lXtst -o vnc vnc.c -g
//引用libvncserver  用于启用服务端
#include <rfb/rfb.h>
#include <stdio.h>
#include <stdlib.h>
#include <algorithm>
#include <unistd.h>
#include <termios.h>

//引用X11库用于抓取桌面,模拟鼠标键盘操作
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/XKBlib.h>
#include <X11/extensions/Xfixes.h>
#include <X11/extensions/XTest.h>

using namespace std;
static rfbCursorPtr myCursor;

//用于绘制鼠标焦点
static const char* cur=
        "                   "
        " x                 "
        " xx                "
        " xxx               "
        " xxxx              "
        " xxxxx             "
        " xxxxxx            "
        " xxxxxxx           "
        " xxxxxxxx          "
        " xxxxxxxxx         "
        " xxxxxxxxxx        "
        " xxxxx             "
        " xx xxx            "
        " x  xxx            "
        "     xxx           "
        "     xxx           "
        "      xxx          "
        "      xxx          "
        "                   ";

static const char* mask=
        "xx                 "
        "xxx                "
        "xxxx               "
        "xxxxx              "
        "xxxxxx             "
        "xxxxxxx            "
        "xxxxxxxx           "
        "xxxxxxxxx          "
        "xxxxxxxxxx         "
        "xxxxxxxxxxx        "
        "xxxxxxxxxxxx       "
        "xxxxxxxxxx         "
        "xxxxxxxx           "
        "xxxxxxxx           "
        "xx  xxxxx          "
        "    xxxxx          "
        "     xxxxx         "
        "     xxxxx         "
        "      xxx          ";


//转换像素数据格式 要不显示颜色异常
//XImage像素顺序RGBA --> 转frameBuffer像素顺序BGRA
void copyImage(const XImage* image, char* buffer, int width, int height, int stride)
{
    if((image == NULL) || (buffer == NULL))
    {
        return;
    }
    char* src = (char*) image->data;
 
    for(int index=0; index< width*height; ++index)
    {
        char single_pixels[4];
        memcpy(single_pixels,src+index*4, 4);
        single_pixels[2]= (src+index*4)[0];
        single_pixels[0]= (src+index*4)[2];
        memcpy(buffer + index * 4, single_pixels, 4);
    }
}

//X11 默认抓取的桌面内容不带鼠标的光标, 需要单独绘制鼠标光标
void paint_mouse_pointer(XImage *image, Display* display, int x_off, int y_off, unsigned int width, unsigned int height)
{
    Display *dpy = display;
    XFixesCursorImage *xcim;
    int x, y;
    int line, column;
    int to_line, to_column;
    int pixstride = image->bits_per_pixel >> 3;

    uint8_t *pix = (uint8_t*)image->data;

    /* Code doesn't currently support 16-bit or PAL8 */
    if (image->bits_per_pixel != 24 && image->bits_per_pixel != 32)
        return;

    xcim = XFixesGetCursorImage(dpy);

    x = xcim->x - xcim->xhot;
    y = xcim->y - xcim->yhot;

    to_line = min((y + xcim->height), (int)(height + y_off));
    to_column = min((x + xcim->width), (int)(width + x_off));

    for (line = max(y, y_off); line < to_line; line++) 
    {
        for (column = max(x, x_off); column < to_column; column++) 
        {
            int  xcim_addr = (line - y) * xcim->width + column - x;
            int image_addr = ((line - y_off) * width + column - x_off) * pixstride;
            int r = (uint8_t)(xcim->pixels[xcim_addr] >>  0);
            int g = (uint8_t)(xcim->pixels[xcim_addr] >>  8);
            int b = (uint8_t)(xcim->pixels[xcim_addr] >> 16);
            int a = (uint8_t)(xcim->pixels[xcim_addr] >> 24);

            if (a == 255) 
            {
                pix[image_addr+0] = r;
                pix[image_addr+1] = g;
                pix[image_addr+2] = b;
            } else if (a) {
                /* pixel values from XFixesGetCursorImage come premultiplied by alpha */
                pix[image_addr+0] = r + (pix[image_addr+0]*(255-a) + 255/2) / 255;
                pix[image_addr+1] = g + (pix[image_addr+1]*(255-a) + 255/2) / 255;
                pix[image_addr+2] = b + (pix[image_addr+2]*(255-a) + 255/2) / 255;
            }
        }
    }
    XFree(xcim);
    xcim = NULL;
}

//生成带鼠标光标的桌面截图
XImage* generateDesktopImageWithCursor(Display* display, Window root, int x, int y, unsigned int width, unsigned int height) 
{
     XImage* image = XGetImage(display, root, x, y, width, height, AllPlanes, ZPixmap);
     paint_mouse_pointer(image,display,x,y,width,height);
     return image;
}

//获取鼠标的位置
bool GetMousePos(int& x, int& y)
{
    Display *dpy;
    Window root;
    Window ret_root;
    Window ret_child;
    int root_x;
    int root_y;
    int win_x;
    int win_y;
    unsigned int mask;
    dpy = XOpenDisplay(NULL);
    root = XDefaultRootWindow(dpy);
    if(XQueryPointer(dpy, root, &ret_root, &ret_child, &root_x, &root_y, &win_x, &win_y, &mask))
    {
        x = root_x;
        y = root_y;
        return true;
    }
    return false;
}

//设置鼠标的位置
bool SetMousePos(const int& x, const int& y){
    Display *dpy = XOpenDisplay(0);
    Window root = XRootWindow(dpy, 0);
    XWarpPointer(dpy, None, root, 0, 0, 0, 0, x, y);
    XFlush(dpy); 
    XCloseDisplay(dpy);
    return true;
}

//模拟鼠标左键按下
bool LeftPress(){
    Display *display = XOpenDisplay(NULL);
    XTestFakeButtonEvent(display, 1, true, 0);
    XFlush(display);
    XCloseDisplay(display);
    return true;
}

//模拟鼠标左键抬起
bool LeftRelease(){
    Display *display = XOpenDisplay(NULL);
    XTestFakeButtonEvent(display, 1, false, 0);
    XFlush(display);
    XCloseDisplay(display);
    return true;
}

//模拟鼠标右键按下
bool RightPress(){
    Display *display = XOpenDisplay(NULL);
    XTestFakeButtonEvent(display, 3, true, 0);
    XFlush(display);
    XCloseDisplay(display);
    return true;
}

//模拟鼠标右键抬起
bool RightRelease(){
    Display *display = XOpenDisplay(NULL);
    XTestFakeButtonEvent(display, 3, false, 0);
    XFlush(display);
    XCloseDisplay(display);
    return true;
}

//模拟鼠标中键按下
bool MiddlePress(){
    Display *display = XOpenDisplay(NULL);
    XTestFakeButtonEvent(display, 2, true, 0);
    XFlush(display);
    XCloseDisplay(display);
    return true;
}

//模拟鼠标中键抬起
bool MiddleRelease(){
    Display *display = XOpenDisplay(NULL);
    XTestFakeButtonEvent(display, 2, false, 0);
    XFlush(display);
    XCloseDisplay(display);
    return true;
}

//模拟滚轮向上滚动
bool WheelUp(){
    Display *display = XOpenDisplay(NULL);
    XTestFakeButtonEvent(display, 5, true, 0);
    XTestFakeButtonEvent(display, 5, false, 0);
    XFlush(display);
    XCloseDisplay(display);
    return true;
}

//模拟滚轮向下滚动
bool WheelDown(){
    Display *display = XOpenDisplay(NULL);
    XTestFakeButtonEvent(display, 4, true, 0);
    XTestFakeButtonEvent(display, 4, false, 0);
    XFlush(display);
    XCloseDisplay(display);
    return true;
}

//模拟其它键按下
bool PressKey(int key){
    Display *display = XOpenDisplay(NULL);
    XTestFakeKeyEvent(display, XKeysymToKeycode(display, key), true, 0);
    XFlush(display);
    XCloseDisplay(display);
    return true;
}

//模拟其它键抬起
bool ReleaseKey(int key){
    Display *display = XOpenDisplay(NULL);
    XTestFakeKeyEvent(display, XKeysymToKeycode(display, key), false, 0);
    XFlush(display);
    XCloseDisplay(display);
    return true;
}

//获取桌面宽度
bool GetScreenWidth(int& w){
    Display* d = XOpenDisplay(NULL);
    Screen* s = DefaultScreenOfDisplay(d);
    w = s->width;
    return true;
}

//获取桌面高度
bool GetScreenHeight(int& h){
    Display* d = XOpenDisplay(NULL);
    Screen* s = DefaultScreenOfDisplay(d);
    h = s->height;
    return true;
}

//判断是否有组合键按下
bool KeyIsDown(int& key){
    XkbStateRec r;
    Display* d = XOpenDisplay(NULL);
    XkbGetState(d, XkbUseCoreKbd, &r);
    if((r.mods & 0x01) && key == 16) //Shift
        return true;
    if((r.mods & 0x04) && key == 17) //Ctrl
        return true;
    if((r.mods & 0x08) && key == 18) //Alt
        return true;
    XCloseDisplay(d);
    return false;
}

//鼠标消息处理
void mouseevent(int buttonMask, int x, int y, rfbClientPtr cl) 
{
    static int oldButtonMask = 0;
    SetMousePos(x, y);

    if(buttonMask && !oldButtonMask)
    {
        if(buttonMask == 1)
            LeftPress();
        if(buttonMask == 2)
            MiddlePress();
        if(buttonMask == 4)
            RightPress();
        if(buttonMask == 8)
            WheelUp();
        if(buttonMask == 16)
            WheelDown();
    }

    if(!buttonMask && oldButtonMask){
        if(oldButtonMask == 1)
            LeftRelease();
        if(oldButtonMask == 2)
            MiddleRelease();
        if(oldButtonMask == 4)
            RightRelease();
    }
    oldButtonMask = buttonMask;
}

//处理按键消息
void keyevent(rfbBool down, rfbKeySym key, rfbClientPtr cl) 
{
    if(down){
        PressKey(key);
    }
    else {
        ReleaseKey(key);
    }
}

int main(int argc, char** argv) 
{
    //开启桌面连接
    Display* disp = XOpenDisplay(NULL);
    if (!disp) 
    {
        printf("open x11 display error\n");
        exit(1);
    }
    //获取桌面窗口
    Window root = DefaultRootWindow(disp);
    XWindowAttributes attrs;
    XGetWindowAttributes(disp, root, &attrs);

    //分配每一帧的内存空间
    char* buffer = (char*) malloc(attrs.width * attrs.height * 4); // RGBA 格式
    if (!buffer) {
        printf("malloc buffer error \n");
        exit(1);
    }

    //使用 libvncserver 创建服务器
    rfbScreenInfoPtr server = rfbGetScreen(&argc, argv, attrs.width, attrs.height, 8, 3, 4);
    server->desktopName = "share desktop server ";
    server->frameBuffer = (char*) buffer;
    server->alwaysShared = true;
    //注册鼠标键盘消息的回调函数
    server->ptrAddEvent = mouseevent;
    server->kbdAddEvent = keyevent;

    //绘制客户端移动的光标
    if(!myCursor) 
    {
        myCursor = rfbMakeXCursor( 19, 19, (char*) cur, (char*) mask);
    }

    server->cursor = myCursor;

    //初始化服务端
    rfbInitServer(server);

    while (true) 
    {
        //每100ms刷新一帧画面内容
        XImage* image = generateDesktopImageWithCursor(disp, root, 0, 0, attrs.width, attrs.height);
        copyImage(image, buffer, attrs.width, attrs.height, server->paddedWidthInBytes);
        rfbMarkRectAsModified(server, 0, 0, server->width, server->height);
        XDestroyImage(image);
        rfbProcessEvents(server, 100000);
    }

    //清理缓存
    XCloseDisplay(disp);
    free(buffer);
    rfbShutdownServer(server, true);
    return 0;
}
