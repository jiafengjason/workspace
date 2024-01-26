/* My program */

#include <getopt.h>
#include <sys/errno.h>
#include <stdio.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <dlfcn.h>
#include <time.h>
#include "libiptc/libiptc.h"
#include "iptables.h"

int main(void)
{
  iptc_handle_t h;
  const char *chain = NULL;
  const char *tablename = NULL;

  program_name = "my_program";
  program_version = NETFILTER_VERSION;

} 
