package main

import (
    "github.com/opencontainers/runc/libcontainer"
    _ "github.com/opencontainers/runc/libcontainer/nsenter"
    "github.com/sirupsen/logrus"
    "os"
    "runtime"
)

func init() {
    if len(os.Args) > 1 && os.Args[1] == "init" {
        runtime.GOMAXPROCS(1)
        runtime.LockOSThread()
        if err := libcontainer.StartInitialization(); err != nil {
            logrus.Fatal(err)
        }
        panic("--this line should have never been executed, congratulations--")
    }
}