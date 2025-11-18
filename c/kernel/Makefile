#KDIR := /lib/modules/$(shell uname -r)/build
KDIR := /usr/src/kernels/$(shell uname -r)/
PWD  := $(shell pwd)

obj-m := kernel_hello.o

all:
	$(MAKE) -C $(KDIR) SUBDIRS=$(PWD) modules

clean:
	rm -f *.o *.ko .*.o.d *~ .*.cmd *.mod.c *.order *.ko.* *.symvers -r .tmp_versions
