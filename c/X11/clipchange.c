//apt-get install libx11-dev libxcomposite-dev libxdamage-dev libxrender-dev
//gcc -o clipchange clipchange.c -lX11 -lXfixes -Wall
#include <stdio.h>
#include <stdlib.h>
#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <X11/extensions/Xfixes.h>

static Time get_timestamp (Display *display, Window window)
{
    XEvent event;
    XChangeProperty (display, window, XA_WM_NAME, XA_STRING, 8, PropModeAppend, NULL, 0);

    while (1) {
        XNextEvent (display, &event);

        if (event.type == PropertyNotify)
            return event.xproperty.time;
    }
}

int main(int argc, char* argv[]){
    Display *display = NULL;
    Window root;
    Window window;
    Window win;
    Time timestamp;
    int black;

    display = XOpenDisplay(NULL);
    Atom CLIPBOARD = XInternAtom(display, "CLIPBOARD", False);
    root = XDefaultRootWindow (display);
    black = BlackPixel (display, DefaultScreen (display));
    window = XCreateSimpleWindow (display, root, 0, 0, 1, 1, 0, black, black);
    XSelectInput (display, window, PropertyChangeMask);


//  XFixesSelectSelectionInput(
//      display, DefaultRootWindow(display), 
//      XA_PRIMARY, XFixesSetSelectionOwnerNotifyMask
//  );

    XFixesSelectSelectionInput(
        display, DefaultRootWindow(display), 
        CLIPBOARD, XFixesSetSelectionOwnerNotifyMask
    );
    
    XEvent event;
    for(;;){
        XNextEvent(display, &event);
        printf("event.type = %d\n", event.type);
        win = XGetSelectionOwner(display, CLIPBOARD);
        printf("xwindow id: 0x%0x\n", win);
        if(win) {
            timestamp = get_timestamp(display, window);
            printf("timestamp: %ld\n", timestamp);
            XSetSelectionOwner(display, CLIPBOARD, None, timestamp);
            XSync (display, False);
            win = XGetSelectionOwner(display, CLIPBOARD);
            printf("xwindow id: 0x%0x\n", win);
        }
    }

    XCloseDisplay(display);
    return 0;
}
