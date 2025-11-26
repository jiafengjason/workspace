#!/usr/bin/env python3
# 超高效版本：单行快速触发
import socket;[socket.socket().connect_ex((h,p)) or socket.socket().close() for h,p in [("8.8.8.8",53),("1.1.1.1",53),("208.67.222.222",53),("8.8.4.4",53),("1.0.0.1",53)]]


