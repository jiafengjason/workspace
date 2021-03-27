/*
yum install libgtk2.0-devel
yum install libwnck-devel
yum install libwnck3-devel
gtk2.0
gcc workspace.c `pkg-config --cflags --libs gtk+-2.0` -o workspace

libwnck 2.31
export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/usr/local/lib/pkgconfig
gcc workspace.c `pkg-config --cflags --libs libwnck-1.0` -o workspace

gcc workspace.c `pkg-config --cflags --libs gtk+-2.0` `pkg-config --cflags --libs libwnck-3.0` -o workspace
*/
#include <gtk/gtk.h>
#include <libwnck/libwnck.h>

WnckMotionDirection direction = WNCK_MOTION_RIGHT;
gint N_WORKSPACES=0;

enum
{
    VIEWPORT_X,
    VIEWPORT_Y,
    N_INFOS
};

GdkPixbuf *create_pixbuf(const gchar * filename)
{
    GdkPixbuf *pixbuf;
    GError *error = NULL;
    pixbuf = gdk_pixbuf_new_from_file(filename, &error);
    if (!pixbuf)
    {
        fprintf(stderr, "%s\n", error->message);
        g_error_free(error);
    }

   return pixbuf;
}

void print_msg(GtkWidget *widget, gpointer window)
{
    g_print("Button clicked\n");
}

GtkWidget *create_toggle_button(void)
{
    GtkWidget *button = gtk_toggle_button_new ();

    gtk_widget_set_can_default (GTK_WIDGET (button), FALSE);
    gtk_widget_set_can_focus (GTK_WIDGET (button), FALSE);
    gtk_button_set_relief (GTK_BUTTON (button), GTK_RELIEF_NONE);
    gtk_button_set_focus_on_click (GTK_BUTTON (button), FALSE);
    gtk_widget_set_name (button, "xfce-panel-toggle-button");

    return button;
}

static void pager_buttons_viewport_button_toggled(GtkWidget *button)
{
    gint *vp_info;

    vp_info = g_object_get_data (G_OBJECT (button), "viewport-info");
    if (G_UNLIKELY (vp_info == NULL))
    {
        g_print("vp_info is null\n");
        return;
    }
    
    g_print("Button X:%d, Y:%d\n", vp_info[VIEWPORT_X], vp_info[VIEWPORT_Y]);
    //wnck_screen_move_viewport(pager->wnck_screen, vp_info[VIEWPORT_X], vp_info[VIEWPORT_Y]);
}

static void on_active_workspace_changed (WnckScreen *screen, WnckWorkspace *previous_workspace)
{
    WnckWorkspace     *active_ws;
    active_ws = wnck_screen_get_active_workspace(screen);
    g_print("Current workspace:name=%s, id=%d, pos=(%d, %d)\n",wnck_workspace_get_name(active_ws), wnck_workspace_get_number(active_ws), wnck_workspace_get_layout_row(active_ws), wnck_workspace_get_layout_column(active_ws));
}

static void on_window_opened(WnckScreen *screen, WnckWindow *window)
{
    GList *windows,*li;
    WnckWindow *wnckWindow;
    WnckWindow *active_window;
    WnckWorkspace *workspace;
    gint index;
    const char *name=NULL;
    
    //wnck_screen_force_update(screen);
    windows = wnck_screen_get_windows(screen);
    active_window = wnck_screen_get_active_window(screen);
    workspace = wnck_window_get_workspace(active_window);
    index = wnck_workspace_get_number(workspace);
    for (li = windows; li != NULL; li = li->next)
    {
        wnckWindow = WNCK_WINDOW (li->data);
        name = wnck_window_get_name(wnckWindow);
        g_print ("%s%s\n", name, wnckWindow == active_window ? " (active)" : "");
        if(strcmp(name, "Workspace")==0)
        {
            g_print ("Window(%s) move from %d to %d\n", name, index, (index+1)%N_WORKSPACES);
            //wnck_window_move_to_workspace(wnckWindow, wnck_screen_get_workspace(screen, (index+1)%N_WORKSPACES));
        }
    }
}

static void on_active_window_changed (WnckScreen *screen, WnckWindow *previously_active_window)
{
    WnckWindow *active_window;
    WnckWorkspace *workspace, *neighbor;
    gint index;
    const char *name=NULL;
    
    active_window = wnck_screen_get_active_window (screen);

    if (active_window)
    {
        name = wnck_window_get_name(active_window);
        g_print ("active: %s\n", name);
        if(strcmp(name, "Desktop")==0)
        {
            return;
        }
        workspace = wnck_window_get_workspace(active_window);
        index = wnck_workspace_get_number(workspace);
        g_print ("workspace: %d\n", index);
        if(index ==3)
        {
            direction = WNCK_MOTION_LEFT;
        }
        neighbor = wnck_workspace_get_neighbor(workspace, direction);
        g_print ("neighbor: %p\n", neighbor);
        wnck_window_move_to_workspace(active_window, neighbor);
    }
    else
        g_print ("no active window\n");
}

int main(int argc, char *argv[])
{
    //WnckWorkspace     *active_ws;
    
    GtkWidget *window;
    GtkWidget *pager;
    GtkWidget *frame;
    GtkWidget *table;
    GtkWidget *button;
    GtkWidget *label;
    GdkPixbuf *icon;
    GtkWidget *halign;
    GdkScreen *gdk_screen;
    GdkDisplay *display;
    WnckScreen *screen;
    WnckWorkspace *workspace;
    WnckWindow *active_window;
    WnckWindow *wnckWindow;
    GdkColormap *colormap;
    GList *windows, *li, *workspaces, *lp;
    gchar          text[30];
    gint           n, n_workspaces;
    gint           screenNum = 0;
    
    gtk_init(&argc, &argv);
    /*
    active_ws = wnck_screen_get_active_workspace (screen);
    if(active_ws==NULL)
    {
        printf("active_ws is NULL!\n");
    }
    */
    wnck_set_client_type (WNCK_CLIENT_TYPE_PAGER);
    
    window = gtk_window_new (GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title (GTK_WINDOW (window), "Workspace");
    gtk_window_set_default_size (GTK_WINDOW (window), 200, 50);
    gtk_window_set_position(GTK_WINDOW(window), GTK_WIN_POS_CENTER);
    icon = create_pixbuf("demo.png");
    gtk_window_set_icon(GTK_WINDOW(window), icon);
    gtk_container_set_border_width(GTK_CONTAINER(window), 15);
    g_signal_connect (window, "destroy", G_CALLBACK(gtk_main_quit), NULL);
    
    //gdk screen
    gdk_screen = gtk_widget_get_screen(window);
    screenNum = gdk_screen_get_number(gdk_screen);
    //g_print("Gdk screen info:%d(%d*%d)\n", screenNum, gdk_screen_get_width(gdk_screen), gdk_screen_get_height(gdk_screen));
    
    //display
    display = gdk_screen_get_display(gdk_screen);
    g_print("Display screen num:%d\n", gdk_display_get_n_screens(display));
    
    //wnck screen
    screen = wnck_screen_get(screenNum);
    wnck_screen_force_update(screen);
    windows = wnck_screen_get_windows(screen);
    g_print("Wnck screen has %d workspaces, %d windows, %d*%d\n",wnck_screen_get_workspace_count(screen), g_list_length(windows), wnck_screen_get_width(screen), wnck_screen_get_height(screen));
    g_signal_connect(G_OBJECT(screen), "active-workspace-changed", G_CALLBACK(on_active_workspace_changed), NULL);
    g_signal_connect(G_OBJECT(screen), "window-opened", G_CALLBACK(on_window_opened), NULL);
    //g_signal_connect(G_OBJECT(screen), "active-window-changed", G_CALLBACK (on_active_window_changed), NULL);
    
    wnck_screen_move_viewport(screen, 1000, 1000);

    //All workspaces
    workspaces = wnck_screen_get_workspaces(screen);
    for (lp = workspaces; lp != NULL; lp = lp->next, n_workspaces++)
    {
        workspace = WNCK_WORKSPACE(lp->data);
        g_print("Worspace(%d) viewport(%d):%d*%d\n", wnck_workspace_get_number(workspace), wnck_workspace_is_virtual(workspace), wnck_workspace_get_viewport_x(workspace), wnck_workspace_get_viewport_y(workspace));
    }
    
    //workspace
    workspace = wnck_screen_get_active_workspace(screen);
    g_print("Current workspace:name=%s, id=%d, pos=(%d, %d)\n",wnck_workspace_get_name(workspace), wnck_workspace_get_number(workspace), wnck_workspace_get_layout_row(workspace), wnck_workspace_get_layout_column(workspace));
    
    //colormap = gdk_screen_get_rgba_colormap(screen);
    //gtk_widget_set_colormap(window, colormap);
    //wnck_screen_change_workspace_count(screen, 1);
    
    //halign = gtk_alignment_new(0, 0, 0, 0);
    //gtk_container_add(GTK_CONTAINER(window), button);
    
    pager = wnck_pager_new(screen);
    wnck_pager_set_display_mode(WNCK_PAGER(pager), WNCK_PAGER_DISPLAY_CONTENT);
    if (!wnck_pager_set_n_rows(WNCK_PAGER(pager), 2))
        g_message ("Setting the pager rows returned false. Maybe the setting is not applied.");

    wnck_pager_set_orientation(WNCK_PAGER(pager), GTK_ORIENTATION_HORIZONTAL);
    //ratio = (gfloat) gdk_screen_width () / (gfloat) gdk_screen_height ();
    wnck_screen_change_workspace_count(screen, N_WORKSPACES);
    gtk_container_add (GTK_CONTAINER(window), pager);
    
    /*
    frame = gtk_frame_new("格状容器排列控件");
    gtk_container_add(GTK_CONTAINER(window),frame);
    
    table = gtk_table_new(1,4,FALSE);
    gtk_container_set_border_width(GTK_CONTAINER(table),10);
    gtk_container_set_border_width(GTK_CONTAINER(table),10);
    //gtk_table_set_row_spacings(GTK_TABLE(table),5);
    //gtk_table_set_col_spacings(GTK_TABLE(table),5);
    gtk_container_add(GTK_CONTAINER(frame),table);

    for (n = 0; n < 4; n++)
    {
        //button = gtk_button_new_with_label("Button");
        //button = gtk_button_new_with_mnemonic("_Button");
        button = create_toggle_button();
        g_snprintf(text, sizeof (text), "Click to switch to Workspace%d", n+1);
        gtk_widget_set_tooltip_text(button, text);
        g_signal_connect (G_OBJECT (button), "toggled", G_CALLBACK(pager_buttons_viewport_button_toggled), NULL);
        g_signal_connect(button, "clicked", G_CALLBACK(print_msg), NULL);
        //button = gtk_button_new_with_label("1");
        gtk_table_attach(GTK_TABLE(table),button,n,n+1,0,1,GTK_FILL | GTK_EXPAND,GTK_FILL | GTK_EXPAND,0,0);
        
        g_snprintf (text, sizeof (text), "%d", n+1);
        label = gtk_label_new (text);
        gtk_label_set_angle(GTK_LABEL (label), 0);
        gtk_container_add (GTK_CONTAINER (button), label);
    }
    */
    //gtk_widget_show (window);
    gtk_widget_show_all(window);
    g_object_unref(icon);
    gtk_main();
    //gtk_widget_hide (window);
    //gtk_main();
    return 0;
}