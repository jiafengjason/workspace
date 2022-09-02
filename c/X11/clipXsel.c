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

typedef struct _MultTrack MultTrack;

struct _MultTrack {
  MultTrack * mparent;
  Display * display;
  Window requestor;
  Atom property;
  Atom selection;
  Time time;
  Atom * atoms;
  unsigned long length;
  unsigned long index;
  unsigned char * sel;
};

/* Selection serving states */
typedef enum {
  S_NULL=0,
  S_INCR_1,
  S_INCR_2
} IncrState;

/* An instance of a selection being served */
typedef struct _IncrTrack IncrTrack;

struct _IncrTrack {
  MultTrack * mparent;
  IncrTrack * prev, * next;
  IncrState state;
  Display * display;
  Window requestor;
  Atom property;
  Atom selection;
  Time time;
  Atom target;
  int format;
  unsigned char * data;
  int nelements; /* total */
  int offset, chunk, max_elements; /* all in terms of nelements */
};

typedef int HandleResult;
#define HANDLE_OK         0
#define HANDLE_ERR        (1<<0)
#define HANDLE_INCOMPLETE (1<<1)
#define DID_DELETE        (1<<2)
#define MAXLINE 4096
#define MAX_PROPERTY_VALUE_LEN 4096

static Display * display;
static Window window;

/* Maxmimum request size supported by this X server */
static long max_req;

static Time timestamp;

static Atom timestamp_atom; /* The TIMESTAMP atom */
static Atom multiple_atom; /* The MULTIPLE atom */
static Atom targets_atom; /* The TARGETS atom */
static Atom delete_atom; /* The DELETE atom */
static Atom incr_atom; /* The INCR atom */
static Atom null_atom; /* The NULL atom */
static Atom text_atom; /* The TEXT atom */
static Atom utf8_atom; /* The UTF8 atom */
static Atom compound_text_atom; /* The COMPOUND_TEXT atom */

#define MAX_NUM_TARGETS 9
static int NUM_TARGETS;
static Atom supported_targets[MAX_NUM_TARGETS];
static sigset_t exit_sigs;
static IncrTrack * incrtrack_list = NULL;

static HandleResult handle_multiple (Display * display, Window requestor, Atom property,
                 unsigned char * sel, Atom selection, Time time,
                 MultTrack * mparent);
static HandleResult process_multiple (MultTrack * mt, Bool do_parent);

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
            {
                XSelectionEvent *xsl = &event.xselection;
                if (xsl->selection != selection) break;

                if (xsl->property == None) {
                    printf("Conversion refused\n");
                    value = NULL;
                    keep_waiting = False;
                } else if (xsl->property == null_atom &&
                    request_target == delete_atom) {
                } else {
                    XGetWindowProperty (xsl->display,
                        xsl->requestor,
                        xsl->property, 0L, 1000000,
                        False, (Atom)AnyPropertyType, &target,
                        &format, &length, &bytesafter, &value);

                    printf("wait_selection, requestor=0x%lx, property=0x%lx (%s), target=0x%lx (%s) length=%ld\n",
                                 xsl->requestor, xsl->property, get_atom_name (xsl->property),
                                 target, get_atom_name(target), length);

                    if (request_target == delete_atom && value == NULL) {
                        keep_waiting = False;
                    } else if (target == incr_atom) {
                        /* Handle INCR transfers */
                        retval = wait_incr_selection (selection, xsl, *(long *)value);
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

                    XDeleteProperty (xsl->display, xsl->requestor, xsl->property);
                }
                break;
            }
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

static void add_incrtrack (IncrTrack * it)
{
    if (incrtrack_list) {
        incrtrack_list->prev = it;
    }
    it->prev = NULL;
    it->next = incrtrack_list;
    incrtrack_list = it;
}

static IncrTrack *fresh_incrtrack (void)
{
    IncrTrack * it;

    it = xs_malloc (sizeof (IncrTrack));
    add_incrtrack (it);

    return it;
}

static void remove_incrtrack (IncrTrack * it)
{
    if (it->prev) {
        it->prev->next = it->next;
    }
    if (it->next) {
        it->next->prev = it->prev;
    }

    if (incrtrack_list == it) {
        incrtrack_list = it->next;
    }
}

static void trash_incrtrack (IncrTrack * it)
{
    remove_incrtrack (it);
    free (it);
}

static IncrTrack *find_incrtrack (Atom atom)
{
    IncrTrack * iti;

    for (iti = incrtrack_list; iti; iti = iti->next) {
        if (atom == iti->property) return iti;
    }

    return NULL;
}

static void notify_incr (IncrTrack * it, HandleResult hr)
{
    XSelectionEvent ev;

    /* Call XSync here to make sure any BadAlloc errors are caught before
    * confirming the conversion. */
    XSync (it->display, False);

    printf("Confirming conversion\n");

    /* Prepare a SelectionNotify event to send, placing the selection in the
    * requested property. */
    ev.type = SelectionNotify;
    ev.display = it->display;
    ev.requestor = it->requestor;
    ev.selection = it->selection;
    ev.time = it->time;
    ev.target = it->target;

    if (hr & HANDLE_ERR) ev.property = None;
    else ev.property = it->property;

    XSendEvent (display, ev.requestor, False, (unsigned long)NULL, (XEvent *)&ev);
}

static void complete_incr (IncrTrack * it, HandleResult hr)
{
    MultTrack * mparent = it->mparent;

    if (mparent) {
        trash_incrtrack (it);
        process_multiple (mparent, True);
    } else {
        notify_incr (it, hr);
        trash_incrtrack (it);
    }
}

static void notify_multiple (MultTrack * mt, HandleResult hr)
{
    XSelectionEvent ev;

    /* Call XSync here to make sure any BadAlloc errors are caught before
    * confirming the conversion. */
    XSync (mt->display, False);

    /* Prepare a SelectionNotify event to send, placing the selection in the
    * requested property. */
    ev.type = SelectionNotify;
    ev.display = mt->display;
    ev.requestor = mt->requestor;
    ev.selection = mt->selection;
    ev.time = mt->time;
    ev.target = multiple_atom;

    if (hr & HANDLE_ERR) ev.property = None;
    else ev.property = mt->property;

    XSendEvent (display, ev.requestor, False, (unsigned long)NULL, (XEvent *)&ev);
}

static void complete_multiple (MultTrack * mt, Bool do_parent, HandleResult hr)
{
    MultTrack * mparent = mt->mparent;

    if (mparent) {
        free (mt);
        if (do_parent) process_multiple (mparent, True);
    } else {
        notify_multiple (mt, hr);
        free (mt);
    }
}

static HandleResult change_property (Display * display, Window requestor, Atom property,
                 Atom target, int format, int mode,
                 unsigned char * data, int nelements,
                 Atom selection, Time time, MultTrack * mparent)
{
    XSelectionEvent ev;
    long nr_bytes;
    IncrTrack * it;

    printf("change_property()\n");

    nr_bytes = nelements * format / 8;

    if (nr_bytes <= max_req) {
        printf("data within maximum request size\n");
        XChangeProperty (display, requestor, property, target, format, mode, data, nelements);

        return HANDLE_OK;
    }

    /* else */
    printf("large data transfer\n");


    /* Send a SelectionNotify event */
    ev.type = SelectionNotify;
    ev.display = display;
    ev.requestor = requestor;
    ev.selection = selection;
    ev.time = time;
    ev.target = target;
    ev.property = property;

    XSelectInput (ev.display, ev.requestor, PropertyChangeMask);

    XChangeProperty (ev.display, ev.requestor, ev.property, incr_atom, 32, PropModeReplace, (unsigned char *)&nr_bytes, 1);

    XSendEvent (display, requestor, False, (unsigned long)NULL, (XEvent *)&ev);

    /* Set up the IncrTrack to track this */
    it = fresh_incrtrack ();

    it->mparent = mparent;
    it->state = S_INCR_1;
    it->display = display;
    it->requestor = requestor;
    it->property = property;
    it->selection = selection;
    it->time = time;
    it->target = target;
    it->format = format;
    it->data = data;
    it->nelements = nelements;
    it->offset = 0;

    /* Maximum nr. of elements that can be transferred in one go */
    it->max_elements = max_req * 8 / format;

    /* Nr. of elements to transfer in this instance */
    it->chunk = MIN (it->max_elements, it->nelements - it->offset);

    /* Wait for that property to get deleted */
    printf("Waiting on initial property deletion (%s)\n", get_atom_name (it->property));

    return HANDLE_INCOMPLETE;
}

static HandleResult incr_stage_1 (IncrTrack * it)
{
    /* First pass: PropModeReplace, from data, size chunk */
    printf("Writing first chunk (%d bytes) (target 0x%lx %s) to property 0x%lx of requestor 0x%lx\n", it->chunk, it->target, get_atom_name(it->target), it->property, it->requestor);
    XChangeProperty (it->display, it->requestor, it->property, it->target, it->format, PropModeReplace, it->data, it->chunk);

    it->offset += it->chunk;

    /* wait for PropertyNotify events */
    printf("Waiting on subsequent deletions ...\n");

    it->state = S_INCR_2;

    return HANDLE_INCOMPLETE;
}

static HandleResult
incr_stage_2 (IncrTrack * it)
{
    it->chunk = MIN (it->max_elements, it->nelements - it->offset);

    if (it->chunk <= 0) {
        /* Now write zero-length data to the property */
        XChangeProperty (it->display, it->requestor, it->property, it->target,
                         it->format, PropModeAppend, NULL, 0);
        it->state = S_NULL;
        printf("Set si to state S_NULL\n");
        return HANDLE_OK;
    } else {
        printf("Writing chunk (%d bytes) to property\n", it->chunk);
        XChangeProperty (it->display, it->requestor, it->property, it->target,
                         it->format, PropModeAppend, it->data+it->offset,
                         it->chunk);
        it->offset += it->chunk;
        printf("%d bytes remaining\n", it->nelements - it->offset);
        return HANDLE_INCOMPLETE;
    }
}

static HandleResult handle_timestamp (Display * display, Window requestor, Atom property,
                  Atom selection, Time time, MultTrack * mparent)
{
    return change_property (display, requestor, property, XA_INTEGER, 32,
                     PropModeReplace, (unsigned char *)&timestamp, 1,
                     selection, time, mparent);
}

static HandleResult handle_targets (Display * display, Window requestor, Atom property,
                Atom selection, Time time, MultTrack * mparent)
{
    Atom * targets_cpy;
    HandleResult r;

    targets_cpy = malloc (sizeof (supported_targets));
    memcpy (targets_cpy, supported_targets, sizeof (supported_targets));

    r = change_property (display, requestor, property, XA_ATOM, 32,
                     PropModeReplace, (unsigned char *)targets_cpy,
                     NUM_TARGETS, selection, time, mparent);
    free(targets_cpy);
    return r;
}

static HandleResult handle_string (Display * display, Window requestor, Atom property,
               unsigned char * sel, Atom selection, Time time, MultTrack * mparent)
{
    return change_property (display, requestor, property, XA_STRING, 8,
                     PropModeReplace, sel, xs_strlen(sel),
                     selection, time, mparent);
}

static HandleResult handle_utf8_string (Display * display, Window requestor, Atom property,
                    unsigned char * sel, Atom selection, Time time, MultTrack * mparent)
{
    return change_property (display, requestor, property, utf8_atom, 8,
                     PropModeReplace, sel, xs_strlen(sel),
                     selection, time, mparent);
}

static HandleResult handle_delete (Display * display, Window requestor, Atom property)
{
    XChangeProperty (display, requestor, property, null_atom, 0,
                   PropModeReplace, NULL, 0);

    return DID_DELETE;
}

static HandleResult process_multiple (MultTrack * mt, Bool do_parent)
{
    HandleResult retval = HANDLE_OK;
    unsigned long i;

    if (!mt) return retval;

    for (; mt->index < mt->length; mt->index += 2) {
        i = mt->index;
        if (mt->atoms[i] == timestamp_atom) {
          retval |= handle_timestamp (mt->display, mt->requestor, mt->atoms[i+1],
                                      mt->selection, mt->time, mt);
        } else if (mt->atoms[i] == targets_atom) {
          retval |= handle_targets (mt->display, mt->requestor, mt->atoms[i+1],
                                    mt->selection, mt->time, mt);
        } else if (mt->atoms[i] == multiple_atom) {
          retval |= handle_multiple (mt->display, mt->requestor, mt->atoms[i+1],
                                     mt->sel, mt->selection, mt->time, mt);
        } else if (mt->atoms[i] == XA_STRING || mt->atoms[i] == text_atom) {
          retval |= handle_string (mt->display, mt->requestor, mt->atoms[i+1],
                                   mt->sel, mt->selection, mt->time, mt);
        } else if (mt->atoms[i] == utf8_atom) {
          retval |= handle_utf8_string (mt->display, mt->requestor, mt->atoms[i+1],
                                        mt->sel, mt->selection, mt->time, mt);
        } else if (mt->atoms[i] == delete_atom) {
          retval |= handle_delete (mt->display, mt->requestor, mt->atoms[i+1]);
        } else if (mt->atoms[i] == None) {
          /* the only other thing we know to handle is None, for which we
           * do nothing. This block is, like, __so__ redundant. Welcome to
           * Over-engineering 101 :) This comment is just here to keep the
           * logic documented and separate from the 'else' block. */
        } else {
          /* for anything we don't know how to handle, we fail the conversion
           * by setting this: */
          mt->atoms[i] = None;
        }

        /* If any of the conversions failed, signify this by setting that
         * atom to None ...*/
        if (retval & HANDLE_ERR) {
          mt->atoms[i] = None;
        }
        /* ... but don't propogate HANDLE_ERR */
        retval &= (~HANDLE_ERR);

        if (retval & HANDLE_INCOMPLETE) break;
    }

    if ((retval & HANDLE_INCOMPLETE) == 0) {
        complete_multiple (mt, do_parent, retval);
    }

    return retval;
}

static HandleResult continue_incr (IncrTrack * it)
{
    HandleResult retval = HANDLE_OK;

    if (it->state == S_INCR_1) {
        retval = incr_stage_1 (it);
    } else if (it->state == S_INCR_2) {
        retval = incr_stage_2 (it);
    }

    /* If that completed the INCR, deal with completion */
    if ((retval & HANDLE_INCOMPLETE) == 0) {
        complete_incr (it, retval);
    }

    return retval;
}

static HandleResult handle_multiple (Display * display, Window requestor, Atom property,
                 unsigned char * sel, Atom selection, Time time, MultTrack * mparent)
{
    MultTrack * mt;
    int format;
    Atom type;
    unsigned long bytesafter;
    HandleResult retval = HANDLE_OK;

    mt = xs_malloc (sizeof (MultTrack));

    XGetWindowProperty (display, requestor, property, 0L, 1000000,
                      False, (Atom)AnyPropertyType, &type,
                      &format, &mt->length, &bytesafter,
                      (unsigned char **)&mt->atoms);

    /* Make sure we got the Atom list we want */
    if (format != 32) return HANDLE_OK;


    mt->mparent = mparent;
    mt->display = display;
    mt->requestor = requestor;
    mt->sel = sel;
    mt->property = property;
    mt->selection = selection;
    mt->time = time;
    mt->index = 0;

    retval = process_multiple (mt, False);

    return retval;
}

Window getParentWindow(Window win)
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

int getWindowPid(Window win)
{
    Atom xa_prop_name;
    Atom xa_ret_type;
    int ret_format;
    unsigned long ret_nitems;
    unsigned long ret_bytes_after;
    unsigned char *ret_prop;
    int pid = 0;

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
            memcpy(&pid, ret_prop, 4);// 类型传换
            printf("window pid: %d\n", pid);
        }
    }

    return pid;
}


static Bool handle_selection_request (XEvent event, unsigned char * sel)
{
    XSelectionRequestEvent * xsr = &event.xselectionrequest;
    XSelectionEvent ev;
    int hr = HANDLE_OK;
    Bool retval = True;

    printf("handle_selection_request, owner=%#lx, requestor=%#lx, property=%#lx (%s), target=%#lx (%s)\n",
               xsr->owner, xsr->requestor,
               xsr->property, get_atom_name (xsr->property),
               xsr->target, get_atom_name (xsr->target));

    ev.type = SelectionNotify;
    ev.display = xsr->display;
    ev.requestor = xsr->requestor;
    ev.selection = xsr->selection;
    ev.time = xsr->time;
    ev.target = xsr->target;
    
    if (xsr->property == None && ev.target != multiple_atom) {
        /* Obsolete requestor */
        xsr->property = xsr->target;
    }

    if (ev.time != CurrentTime && ev.time < timestamp) {
        /* If the time is outside the period we have owned the selection,
        * which is any time later than timestamp, or if the requested target
        * is not a string, then refuse the SelectionRequest. NB. Some broken
        * clients don't set a valid timestamp, so we have to check against
        * CurrentTime here. */
        ev.property = None;
        printf("timestamp expired:ev.time=%ld timestamp=%ld\n", ev.time, timestamp);
    } else if (ev.target == timestamp_atom) {
        /* Return timestamp used to acquire ownership if target is TIMESTAMP */
        ev.property = xsr->property;
        hr = handle_timestamp (ev.display, ev.requestor, ev.property,
                             ev.selection, ev.time, NULL);
    } else if (ev.target == targets_atom) {
        /* Return a list of supported targets (TARGETS)*/
        ev.property = xsr->property;
        hr = handle_targets (ev.display, ev.requestor, ev.property,
                           ev.selection, ev.time, NULL);
    } else if (ev.target == multiple_atom) {
        if (xsr->property == None) { /* Invalid MULTIPLE request */
            ev.property = None;
        } else {
            /* Handle MULTIPLE request */
            ev.property = xsr->property;
            hr = handle_multiple (ev.display, ev.requestor, ev.property, sel,
                                  ev.selection, ev.time, NULL);
        }
    } else if (ev.target == XA_STRING || ev.target == text_atom) {
        /* Received STRING or TEXT request */
        ev.property = xsr->property;
        hr = handle_string (ev.display, ev.requestor, ev.property, sel,
                          ev.selection, ev.time, NULL);
    } else if (ev.target == utf8_atom) {
        /* Received UTF8_STRING request */
        ev.property = xsr->property;
        hr = handle_utf8_string (ev.display, ev.requestor, ev.property, sel,
                               ev.selection, ev.time, NULL);
    } else if (ev.target == delete_atom) {
        /* Received DELETE request */
        ev.property = xsr->property;
        hr = handle_delete (ev.display, ev.requestor, ev.property);
        retval = False;
    } else {
        /* Cannot convert to requested target. This includes most non-string
        * datatypes, and INSERT_SELECTION, INSERT_PROPERTY */
        ev.property = None;
    }
    
    /* Return False if a DELETE was processed */
    retval = (hr & DID_DELETE) ? False : True;
    
    /* If there was an error in the transfer, it should be refused */
    if (hr & HANDLE_ERR) {
      printf("Error in transfer\n");
      ev.property = None;
    }

    if (getWindowPid(ev.requestor)) {
        ev.property = None;
    }

    if ((hr & HANDLE_INCOMPLETE) == 0) {
      if (ev.property == None) {printf("Refusing conversion\n");}
      else { printf("Confirming conversion\n");}

      XSendEvent (display, ev.requestor, False, (unsigned long)NULL, (XEvent *)&ev);
    
      /* If we return False here, we may quit immediately, so sync out the X queue. */
      if (!retval) XSync (display, False);
    }
    
    return retval;
}

void set_selection (Atom selection, unsigned char * sel)
{
    XEvent event;
    IncrTrack * it;

    if (own_selection(selection) == False) return;

    for (;;) {
        /* Flush before unblocking signals so we send replies before exiting */
        XFlush (display);
        unblock_exit_sigs ();
        XNextEvent (display, &event);
        block_exit_sigs ();

        printf("set_selection event.type = %d\n", event.type);

        switch (event.type) {
        case SelectionClear:
            if (event.xselectionclear.selection == selection) return;
            break;
        case SelectionRequest:
            if (event.xselectionrequest.selection != selection) break;

            if (!handle_selection_request (event, sel)) return;
            break;
        case PropertyNotify:
            if (event.xproperty.state != PropertyDelete) break;

            it = find_incrtrack (event.xproperty.atom);
            if (it != NULL) {
                continue_incr (it);
            }
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
    XEvent event;
    unsigned char *sel = NULL;
    int s=0;
    int ev_base = 0;
    int err_base = 0;
    XFixesSelectionNotifyEvent *xfsn = NULL;

    display = XOpenDisplay(NULL);
    Atom selection = XInternAtom(display, "CLIPBOARD", False);
    root = XDefaultRootWindow (display);
    black = BlackPixel (display, DefaultScreen (display));
    window = XCreateSimpleWindow (display, root, 0, 0, 1, 1, 0, black, black);
    printf("Window id: %#lx (unmapped)\n", window);
    XStoreName(display, window, "xsel");

    XSelectInput (display, window, PropertyChangeMask);

    /* Get the maximum incremental selection size in bytes */
    /*max_req = MAX_SELECTION_INCR (display);*/
    max_req = 4000;

      NUM_TARGETS=0;

    timestamp_atom = XInternAtom (display, "TIMESTAMP", False);
    supported_targets[s++] = timestamp_atom;
    NUM_TARGETS++;
    multiple_atom = XInternAtom (display, "MULTIPLE", False);
    supported_targets[s++] = multiple_atom;
    NUM_TARGETS++;
    targets_atom = XInternAtom (display, "TARGETS", False);
    supported_targets[s++] = targets_atom;
    NUM_TARGETS++;
    delete_atom = XInternAtom (display, "DELETE", False);
    supported_targets[s++] = delete_atom;
    NUM_TARGETS++;
    incr_atom = XInternAtom (display, "INCR", False);
    supported_targets[s++] = incr_atom;
    NUM_TARGETS++;
    text_atom = XInternAtom (display, "TEXT", False);
    supported_targets[s++] = text_atom;
    NUM_TARGETS++;
    utf8_atom = XInternAtom (display, "UTF8_STRING", True);
    if(utf8_atom != None) {
        supported_targets[s++] = utf8_atom;
        NUM_TARGETS++;
    } else {
        utf8_atom = XA_STRING;
    }
    supported_targets[s++] = XA_STRING;
    NUM_TARGETS++;
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
        timestamp = get_timestamp();
        XNextEvent(display, &event);
        printf("main event.type = %d\n", event.type);
        //owner = XGetSelectionOwner(display, selection);
        //printf("Main xwindow id: 0x%0lx\n", owner);
        if (event.type==ev_base + XFixesSelectionNotify) {
            xfsn = (XFixesSelectionNotifyEvent *)&event;
            printf("owner=0x%0lx window=0x%0lx\n", xfsn->owner, window);
            if(xfsn->owner!=window) {
                sel = get_selection_text(selection);
                set_selection(selection, sel);
            }
        }
    }

    XCloseDisplay(display);
    return 0;
}
