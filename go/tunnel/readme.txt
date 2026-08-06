1、修改控制器配置文件内容：/home/enlink/app/nginx/conf/vhost/sdp-web-admin.conf，重启nginx
docker restart nginx

2、网关上导入session会话信息
sh session2.0.sh

3、隧道压测
./tunnel -gatewayhost 192.168.108.55 -port 58679 -speed_n 500 -index 0 -tunnel_n 20000 -proto udp -dip 192.168.112.142 -dport 12345 -pps 10
-gatewayhost    #网关地址
-port           #网关业务端口
-speed_n        #每秒新建隧道数，默认为1
-index          #隧道起始session index，用于多台配合打流，默认为0
-tunnel_n       #新建隧道总数
-proto          #隧道协议，默认udp
-dip            #隧道应用ip
-dport          #隧道应用端口
-pps            #每秒数据包数，默认为1