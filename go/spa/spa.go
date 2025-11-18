package main

/*
#cgo CFLAGS: -Iinclude
#cgo LDFLAGS: -Llib -Wl,-rpath=lib -lfko
#include "fko.h"
#include <string.h>
#include <stdlib.h>
*/
import "C"
import (
	"fmt"
	"unsafe"
)

func main() {
	ip := C.CString("127.0.0.1")
	defer C.free(unsafe.Pointer(ip))

	spaKey := C.CString("ffcbbd5d0ff16b8d161b80a8be26b918")
	defer C.free(unsafe.Pointer(spaKey))

	devid := C.CString("enlink")
	defer C.free(unsafe.Pointer(devid))

	res := C.fko_send_spa_data(ip, C.int(6789), spaKey, C.int(62201), devid)
	if res != C.FKO_SUCCESS {
		fmt.Println("fail")
	}

	fmt.Println(res)
}





