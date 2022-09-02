#KDIR := /lib/modules/$(shell uname -r)/build
KDIR := /usr/src/kernels/3.10.0-1160.59.1.el7.x86_64/
PWD  := $(shell pwd)

obj-m := mini_firewall.o

all:
	$(MAKE) -C $(KDIR) SUBDIRS=$(PWD) modules

clean:
	rm -f *.o *.ko .*.o.d *~ .*.cmd *.mod.c *.order *.ko.* *.symvers -r .tmp_versions
