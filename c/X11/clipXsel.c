//apt-get install libx11-dev libxcomposite-dev libxdamage-dev libxrender-dev
//gcc -o clipXsel clipXsel.c -lX11 -lXfixes -Wall
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <syslog.h>
#include <sys/param.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <X11/extensions/Xfixes.h>

#define HANDLE_OK         0
#define HANDLE_ERR        (1<<0)
#define HANDLE_INCOMPLETE (1<<1)
#define DID_DELETE        (1<<2)
#define MAXLINE 4096

static Display * display;
static Window window;

static Atom timestamp_atom; /* The TIMESTAMP atom */
static Atom multiple_atom; /* The MULTIPLE atom */
static Atom targets_atom; /* The TARGETS atom */
static Atom delete_atom; /* The DELETE atom */
static Atom incr_atom; /* The INCR atom */
static Atom null_atom; /* The NULL atom */
static Atom text_atom; /* The TEXT atom */
static Atom utf8_atom; /* The UTF8 atom */
static Atom compound_text_atom; /* The COMPOUND_TEXT atom */

static sigset_t exit_sigs;

static Time get_timestamp()
{
    XEvent event;
    XChangeProperty (display, window, XA_WM_NAME, XA_STRING, 8, PropModeAppend, NULL, 0);

    while (1) {
        XNextEvent (display, &event);

        if (event.type == PropertyNotify)
            return event.xproperty.time;
    }
}

static char *get_atom_name (Atom atom)
{
    char * ret;
    static char atom_name[MAXLINE+2];  /* unused extra char to avoid
                                        string-op-truncation warning */

    if (atom == None) return "None";
    if (atom == XA_STRING) return "STRING";
    if (atom == XA_PRIMARY) return "PRIMARY";
    if (atom == XA_SECONDARY) return "SECONDARY";
    if (atom == timestamp_atom) return "TIMESTAMP";
    if (atom == multiple_atom) return "MULTIPLE";
    if (atom == targets_atom) return "TARGETS";
    if (atom == delete_atom) return "DELETE";
    if (atom == incr_atom) return "INCR";
    if (atom == null_atom) return "NULL";
    if (atom == text_atom) return "TEXT";
    if (atom == utf8_atom) return "UTF8_STRING";

    ret = XGetAtomName (display, atom);
    strncpy (atom_name, ret, MAXLINE+1);
    if (atom_name[MAXLINE] != '\0')
    {
        atom_name[MAXLINE-3] = '.';
        atom_name[MAXLINE-2] = '.';
        atom_name[MAXLINE-1] = '.';
        atom_name[MAXLINE] = '\0';
    }
    XFree (ret);

    return atom_name;
}

/*
 * xs_malloc (size)
 *
 * Malloc wrapper. Always returns a successful allocation. Exits if the
 * allocation didn't succeed.
 */
static void *
xs_malloc (size_t size)
{
    void * ret;

    if (size == 0) size = 1;
    if ((ret = malloc (size)) == NULL) {
        printf("malloc error\n");
        exit(1);
    }

    return ret;
}

/*
 * xs_strdup (s)
 *
 * strdup wrapper for unsigned char *
 */
#define xs_strdup(s) ((unsigned char *) _xs_strdup ((const char *)s))
static char * _xs_strdup (const char * s)
{
    char * ret;

    if (s == NULL) return NULL;
    if ((ret = strdup(s)) == NULL) {
        printf("strdup error\n");
        exit(1);
    }

    return ret; 
}

/*
 * xs_strlen (s)
 *
 * strlen wrapper for unsigned char *
 */
#define xs_strlen(s) (strlen ((const char *) s))

/*
 * xs_strncpy (s)
 *
 * strncpy wrapper for unsigned char *
 */
#define xs_strncpy(dest,s,n) (_xs_strncpy ((char *)dest, (const char *)s, n))
static char *
_xs_strncpy (char * dest, const char * src, size_t n)
{
    if (n > 0) {
        strncpy (dest, src, n-1);
        dest[n-1] = '\0';
    }
    return dest;
}

void init_deamon()
{
    int pid;
    int i;

    pid=fork();
    if(pid>0)
        exit(0);//是父进程，结束父进程
    else if(pid<0)
        exit(1);//fork失败，退出

    //是第一子进程，后台继续执行
    setsid();//第一子进程成为新的会话组长和进程组长
    //并与控制终端分离

    pid=fork();
    if(pid>0)
        exit(0);//是第一子进程，结束第一子进程
    else if(pid<0)
        exit(1);//fork失败，退出

    //是第二子进程，继续
    //第二子进程不再是会话组长
    for(i=0;i< NOFILE;++i)//关闭打开的文件描述符
        close(i);

    chdir("/tmp");//改变工作目录到/
    umask(0);//重设文件创建掩模
}

static Bool own_selection (Atom selection)
{
    Window owner;

    XSetSelectionOwner(display, selection, window, CurrentTime);
    /* XGetSelectionOwner does a round trip to the X server, so there is no need to call XSync here. */
    owner = XGetSelectionOwner (display, selection);
    if (owner != window) {
        printf("XGetSelectionOwner failed:xwindow id: 0x%0lx\n", owner);
        return False;
    } else {
        //XSetErrorHandler (handle_x_errors);
        return True;
    }
}

static void block_exit_sigs(void)
{
    sigprocmask(SIG_BLOCK, &exit_sigs, NULL);
}

static void unblock_exit_sigs(void)
{
    sigprocmask(SIG_UNBLOCK, &exit_sigs, NULL);
}

static Bool get_append_property (XSelectionEvent * xsl, unsigned char ** buffer,
                     unsigned long * offset, unsigned long * alloc)
{
  unsigned char * ptr;
  Atom target;
  int format;
  unsigned long bytesafter, length;
  unsigned char * value;

  XGetWindowProperty (xsl->display, xsl->requestor, xsl->property,
                      0L, 1000000, True, (Atom)AnyPropertyType,
                      &target, &format, &length, &bytesafter, &value);

  printf("wait_selection, requestor=0x%lx, property=0x%lx (%s), target=0x%lx (%s) length=%ld\n",
               xsl->requestor, xsl->property, get_atom_name (xsl->property),
               target, get_atom_name(target), length);

  if (target != XA_STRING && target != utf8_atom &&
      target != compound_text_atom) {
    printf("target %s not XA_STRING nor UTF8_STRING in get_append_property()", get_atom_name (target));
    free (*buffer);
    *buffer = NULL;
    return False;
  } else if (length == 0) {
    /* A length of 0 indicates the end of the transfer */
    printf("Got zero length property; end of INCR transfer\n");
    return False;
  } else if (format == 8) {
    if (*offset + length + 1 > *alloc) {
      *alloc = *offset + length + 1;
      if ((*buffer = realloc (*buffer, *alloc)) == NULL) {
        printf("realloc error\n");
        exit(1);
      }
    }
    ptr = *buffer + *offset;
    memcpy (ptr, value, length);
    ptr[length] = '\0';
    *offset += length;
    printf("Appended %ld bytes to buffer\n", length);
  } else {
    printf("Retrieved non-8-bit data\n");
  }

  return True;
}

static unsigned char *wait_incr_selection (Atom selection, XSelectionEvent * xsl, int init_alloc)
{
    XEvent event;
    unsigned char * incr_base = NULL, * incr_ptr = NULL;
    unsigned long incr_alloc = 0, incr_xfer = 0;
    Bool wait_prop = True;

    printf("Initialising incremental retrieval of at least %d bytes\n", init_alloc);

    /* Take an interest in the requestor */
    XSelectInput (xsl->display, xsl->requestor, PropertyChangeMask);

    incr_alloc = init_alloc;
    incr_base = xs_malloc (incr_alloc);
    incr_ptr = incr_base;

    printf("Deleting property that informed of INCR transfer\n");
    XDeleteProperty (xsl->display, xsl->requestor, xsl->property);

    printf("Waiting on PropertyNotify events\n");
    while (wait_prop) {
        XNextEvent (xsl->display, &event);

        switch (event.type) {
        case PropertyNotify:
          if (event.xproperty.state != PropertyNewValue) break;

          wait_prop = get_append_property (xsl, &incr_base, &incr_xfer, &incr_alloc);
          break;
        default:
          break;
        }
    }

    /* when zero length found, finish up & delete last */
    XDeleteProperty (xsl->display, xsl->requestor, xsl->property);

    printf("Finished INCR retrieval\n");

    return incr_base;
}

static unsigned char *wait_selection (Atom selection, Atom request_target)
{
    XEvent event;
    Atom target;
    int format;
    unsigned long bytesafter, length;
    unsigned char * value, * retval = NULL;
    Bool keep_waiting = True;

    while (keep_waiting) {
        XNextEvent (display, &event);

        printf("wait_selection event.type = %d\n", event.type);
        switch (event.type) {
            case SelectionNotify:
                XSelectionEvent *xsl = &event.xselection;
                if (event.xselection.selection != selection) break;

                if (event.xselection.property == None) {
                    printf("Conversion refused\n");
                    value = NULL;
                    keep_waiting = False;
                } else if (event.xselection.property == null_atom &&
                    request_target == delete_atom) {
                } else {
                    XGetWindowProperty (event.xselection.display,
                        event.xselection.requestor,
                        event.xselection.property, 0L, 1000000,
                        False, (Atom)AnyPropertyType, &target,
                        &format, &length, &bytesafter, &value);

                    printf("wait_selection, requestor=0x%lx, property=0x%lx (%s), target=0x%lx (%s) length=%ld\n",
                                 xsl->requestor, xsl->property, get_atom_name (xsl->property),
                                 target, get_atom_name(target), length);

                    if (request_target == delete_atom && value == NULL) {
                        keep_waiting = False;
                    } else if (target == incr_atom) {
                        /* Handle INCR transfers */
                        retval = wait_incr_selection (selection, &event.xselection, *(long *)value);
                        keep_waiting = False;
                    } else if (target != utf8_atom && target != XA_STRING &&
                               target != compound_text_atom &&
                               request_target != delete_atom) {
                        /* Report non-TEXT atoms */
                        printf("Selection (type %s) is not a string.\n", get_atom_name (target));
                        free (retval);
                        retval = NULL;
                        keep_waiting = False;
                    } else {
                        retval = xs_strdup (value);
                        XFree (value);
                        keep_waiting = False;
                    }

                    XDeleteProperty (event.xselection.display,
                                     event.xselection.requestor,
                                     event.xselection.property);
      }
      break;
    default:
      break;
    }
  }

  return retval;
}

static unsigned char *get_selection (Atom selection, Atom request_target)
{
    Atom prop;
    unsigned char * retval;

    prop = XInternAtom (display, "XSEL_DATA", False);
    XConvertSelection (display, selection, request_target, prop, window, CurrentTime);
    XSync (display, False);

    retval = wait_selection (selection, request_target);

    return retval;
}

static unsigned char *get_selection_text (Atom selection)
{
    unsigned char * retval;

    if ((retval = get_selection (selection, utf8_atom)) == NULL)
        retval = get_selection (selection, XA_STRING);

    printf("get_selection_text:%s\n", retval);

    return retval;
}

static Bool handle_selection_request (XEvent event, unsigned char * sel)
{
    XSelectionRequestEvent * xsr = &event.xselectionrequest;
    XSelectionEvent ev;
    int hr = HANDLE_OK;
    Bool retval = True;

    printf("handle_selection_request, property=0x%lx (%s), target=0x%lx (%s)\n",
               xsr->property, get_atom_name (xsr->property),
               xsr->target, get_atom_name (xsr->target));
    return True;
}

void set_selection (Atom selection, unsigned char * sel)
{
    XEvent event;

    if (own_selection(selection) == False) return;

    for (;;) {
        /* Flush before unblocking signals so we send replies before exiting */
        XFlush (display);
        unblock_exit_sigs ();
        XNextEvent (display, &event);
        block_exit_sigs ();

        printf("set_selection event.type = %d\n", event.type);

        switch (event.type) {
        case SelectionRequest:
            if (event.xselectionrequest.selection != selection) break;

            if (!handle_selection_request (event, sel)) return;
        
            break;
        default:
            break;
        }
    }
}

int main(int argc, char* argv[]){
    Window root;
    //Window owner;
    int black;
    //Time timestamp;
    XEvent event;
    unsigned char *sel = NULL;
    int ev_base = 0;
    int err_base = 0;
    XFixesSelectionNotifyEvent *ev;

    display = XOpenDisplay(NULL);
    Atom selection = XInternAtom(display, "CLIPBOARD", False);
    root = XDefaultRootWindow (display);
    black = BlackPixel (display, DefaultScreen (display));
    window = XCreateSimpleWindow (display, root, 0, 0, 1, 1, 0, black, black);
    XSelectInput (display, window, PropertyChangeMask);

    timestamp_atom = XInternAtom (display, "TIMESTAMP", False);
    multiple_atom = XInternAtom (display, "MULTIPLE", False);
    targets_atom = XInternAtom (display, "TARGETS", False);
    delete_atom = XInternAtom (display, "DELETE", False);
    incr_atom = XInternAtom (display, "INCR", False);
    text_atom = XInternAtom (display, "TEXT", False);
    utf8_atom = XInternAtom (display, "UTF8_STRING", True);
    if(utf8_atom != None) {
    } else {
      utf8_atom = XA_STRING;
    }
    null_atom = XInternAtom (display, "NULL", False);
    compound_text_atom = XInternAtom (display, "COMPOUND_TEXT", False);

    sigemptyset (&exit_sigs);
    sigaddset (&exit_sigs, SIGALRM);
    sigaddset (&exit_sigs, SIGINT);
    sigaddset (&exit_sigs, SIGTERM);

//  XFixesSelectSelectionInput(
//      display, DefaultRootWindow(display), 
//      XA_PRIMARY, XFixesSetSelectionOwnerNotifyMask
//  );

    XFixesQueryExtension(display, &ev_base, &err_base);
    XFixesSelectSelectionInput(display, DefaultRootWindow(display), selection, XFixesSetSelectionOwnerNotifyMask);
    for(;;){
        XNextEvent(display, &event);
        printf("main event.type = %d\n", event.type);
        //owner = XGetSelectionOwner(display, selection);
        //printf("Main xwindow id: 0x%0lx\n", owner);
        if (event.type == ev_base + XFixesSelectionNotify) {
            ev = (XFixesSelectionNotifyEvent *)&event;
            printf("owner=0x%0lx window=0x%0lx\n", ev->owner, window);
            if(ev->owner!=window) {
                //timestamp = get_timestamp();
                sel = get_selection_text(selection);
                set_selection(selection, sel);
            }
        }
    }

    XCloseDisplay(display);
    return 0;
}
