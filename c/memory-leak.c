// export ASAN_OPTIONS=halt_on_error=0:use_sigaltstack=0:detect_leaks=1:malloc_context_size=15:log_path=/var/log/asan.log
// /usr/bin/gcc memory-leak.c -o memory-leak -lasan -g -fsanitize=address -fsanitize-recover=address -fsanitize=leak 
#include <stdlib.h>

void *p;

int main() {
  p = malloc(7);
  p = 0; // The memory is leaked here.
  return 0;
}
