EXTRA_CFLAGS := -g
obj-m += my_debugfs.o

default:
	make -C /lib/modules/$(shell uname -r)/build/ SUBDIRS=$(shell pwd) modules 
