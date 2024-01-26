package main

import (
	"bytes"
	"crypto/tls"
	"encoding/binary"
	//"encoding/json"
	//"encoding/xml"
	enerr "errors"
	"fmt"
	//"github.com/snail007/goproxy/utils"
	"io"
	"io/ioutil"
	"log"
	"net"
	"net/http"
	"os"
	"strconv"
	"strings"
    //"math/rand"
	"time"
        "flag"
        "crypto/md5"
    //"encoding/hex"
    //"net/http/cookiejar"
	"math/rand"
    //"bufio"
	//"path/filepath"
)

func md5V2(str string) string {
    data := []byte(str)
    has := md5.Sum(data)
    md5str := fmt.Sprintf("%x", has)
    return md5str
}

type UDP struct {
	Sport uint16
	Dport uint16
	Len   uint16
	Checksum uint16
}

type ICMP struct {
	Type        uint8
	Code        uint8
	Checksum    uint16
	Identifier  uint16
	SequenceNum uint16
}

const (
	Version      = 4  // protocol version
	HeaderLen    = 20 // header length without extension headers
	maxHeaderLen = 60 // sensible default, revisit if later RFCs define new usage of version and header length fields
)

type HeaderFlags int

const (
	MoreFragments HeaderFlags = 1 << iota // more fragments flag
	DontFragment                          // don't fragment flag
)

type V6Header struct {
    Version  int
    Priority int
    Flowlbl  [3]byte
    Len      int
    NextHdr  int
    Hoblimit int
    Src      net.IP
    Dst      net.IP
}

func (h *V6Header) Marshal() ([]byte) {
    if h == nil {
        return nil
    }

    b := make([]byte, 40) //ipv6 header len = 40
	b[0] = byte(6<<4 | (0 >> 2 & 0x0f))
    b[1] = byte(0)
    b[2] = byte(0)
    b[3] = byte(0)
    binary.BigEndian.PutUint16(b[4:6], uint16(h.Len))
    b[6] = byte(17)
    b[7] = byte(64)

	if ip := h.Src.To16(); ip != nil {
		copy(b[8:24], ip[:net.IPv6len])
	}

	if ip := h.Dst.To16(); ip != nil {
		copy(b[24:40], ip[:net.IPv6len])
	}

    return b
}

type Header struct {
	Version  int         // protocol version
	Len      int         // header length
	TOS      int         // type-of-service
	TotalLen int         // packet total length
	ID       int         // identification
	Flags    HeaderFlags // flags
	FragOff  int         // fragment offset
	TTL      int         // time-to-live
	Protocol int         // next protocol
	Checksum int         // checksum
	Src      net.IP      // source address
	Dst      net.IP      // destination address
	Options  []byte      // options, extension headers
}

func (h *Header) Marshal() ([]byte) {
	if h == nil {
		return nil
	}
	if h.Len < HeaderLen {
		return nil
	}
	hdrlen := HeaderLen + len(h.Options)
	b := make([]byte, hdrlen)
	b[0] = byte(Version<<4 | (hdrlen >> 2 & 0x0f))
	b[1] = byte(h.TOS)
	flagsAndFragOff := (h.FragOff & 0x1fff) | int(h.Flags<<13)

    binary.BigEndian.PutUint16(b[2:4], uint16(h.TotalLen))
    binary.BigEndian.PutUint16(b[6:8], uint16(flagsAndFragOff))

	binary.BigEndian.PutUint16(b[4:6], uint16(h.ID))
	b[8] = byte(h.TTL)
	b[9] = byte(h.Protocol)
	binary.BigEndian.PutUint16(b[10:12], uint16(h.Checksum))
	if ip := h.Src.To4(); ip != nil {
		copy(b[12:16], ip[:net.IPv4len])
	}
	if ip := h.Dst.To4(); ip != nil {
		copy(b[16:20], ip[:net.IPv4len])
	} else {
		return nil
	}
	if len(h.Options) > 0 {
		copy(b[HeaderLen:], h.Options)
	}
	return b
}

type LoginBody struct {
	Msg       string `json:"msg"`
	Token     string `json:"token"`
	Server    string `json:"server"`
	GatedPort struct {
		GatedPort   int `json:"gated_port"`
		ServicePort int `json:"service_port"`
	} `json:"gated_port"`
	Status int `json:"status"`
	Data   []struct {
		UserLocalIP         string      `json:"user_local_ip"`
		RuleID              string      `json:"rule_id"`
		Status              string      `json:"status"`
		Email               string      `json:"email"`
		IsSyncGroupRule     int         `json:"is_sync_group_rule"`
		IsBilling           int         `json:"is_billing"`
		HostIP              string      `json:"host_ip"`
		Domian              string      `json:"domian"`
		OperatorType        int         `json:"operator_type"`
		HardwareFeatureCode string      `json:"hardware_feature_code"`
		DeleteTime          interface{} `json:"delete_time"`
		AuthType            string      `json:"auth_type"`
		GroupName           string      `json:"group_name"`
		Type                int         `json:"type"`
		UpdateOperator      int         `json:"update_operator"`
		HardWareID          string      `json:"hard_ware_id"`
		ID                  string      `json:"id"`
		ServiceIP           string      `json:"service_ip"`
		CreateTime          string      `json:"create_time"`
		Tel                 string      `json:"tel"`
		UpdateTime          string      `json:"update_time"`
		PwdModifyTime       string      `json:"pwd_modify_time"`
		SessionTimeout      int         `json:"session_timeout"`
		LoginTime           int64       `json:"login_time"`
		AuthID              string      `json:"auth_id"`
		SecretKey           string      `json:"secret_key"`
		FullName            string      `json:"full_name"`
		UserName            string      `json:"user_name"`
		TokenSerialNum      string      `json:"token_serial_num"`
		DeleteOperator      int         `json:"delete_operator"`
		DeleteFlag          int         `json:"delete_flag"`
		CreateOperator      int         `json:"create_operator"`
		Password            string      `json:"password"`
		GroupID             string      `json:"group_id"`
	} `json:"data"`
	Version struct {
		Time        int         `json:"time"`
		Remark      interface{} `json:"remark"`
		ShowVersion string      `json:"show_version"`
		ID          int         `json:"id"`
		ForceUpdate int         `json:"force_update"`
		Type        int         `json:"type"`
		Version     int         `json:"version"`
	} `json:"version"`
}

type INFO_FROM_REMOTE_SERVER struct {
	ip      string
	mask    string
	gateway string
	dns_ip  string
	len_dns uint
	dns     []string //www.baidu.com;
	len_ip  uint
	iplist  []string //192.178.2.2:9000；
	ip_v6   string
	dns_ipv6  string
}

var (
    IPv4    = net.IPv4(0, 0, 0, 0) // all zeros
	IPv6    = net.IP{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}
	DnsIPv6 = net.IP{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}
    GatewayHost string
)
//var curCookies []*http.Cookie = nil;
//var gCurCookies []*http.Cookie = nil;
//var gCurCookieJar *cookiejar.Jar;

/*
func initAll(){
    gCurCookies = nil
    //var err error;
    gCurCookieJar,_ = cookiejar.New(nil)
}
*/

func connectTLS(server string) (*tls.Conn, error) {
	conf := &tls.Config{
		InsecureSkipVerify: true,
	}
	a := strings.Split(string(server), ":")
	if cap(a) >= 2 { // v6
		address := "[" + server + "]" + ":443"
		conn, err := tls.Dial("tcp6", address, conf)
		if err != nil {
			log.Println("[server] Connect server use Ipv6 adress error ", err)
			return conn, err
		}
		state := conn.ConnectionState()
		log.Println("[server] Ipv6 Handshaked: ", state.HandshakeComplete)
		return conn, err
	} else {
		address := server + ":443"
		conn, err := tls.Dial("tcp", address, conf)
		if err != nil {
			log.Println("[server] Connect server use Ipv4 adress error ", err)
			return conn, err
		}
		state := conn.ConnectionState()
		log.Println("[server] Ipv4 Handshaked: ", state.HandshakeComplete)
		return conn, err
	}
}

func auth(name string, sessionId string) []byte {

	ELK_VERSION := []byte{0x01}
	ELK_PROTO := []byte{0x01}
	//TODO:注意验证网络字节序问题
	//包总长度占位符，所有数据填充完毕后，计算长度，重新设置这两个字节
	ELK_PACKAGE_LEN := []byte{0x00, 0x00}
	ELK_EXTENT_ZERO := []byte{0x00, 0x00, 0x00, 0x00}
	ELK_METHOD_STUN := []byte{0x01, 0x00, 0x00, 0x00}
	//该值为user@groupId
	ELK_OPT_USERNAME := []byte{0x01, 0x00}
	ELK_OPT_SESSID := []byte{0x02, 0x00}

	p := bytes.NewBuffer(ELK_VERSION)
	p.Write(ELK_PROTO)
	//TODO:注意验证网络字节序问题
	//包总长度占位符，所有数据填充完毕后，计算长度，重新设置这两个字节
	p.Write(ELK_PACKAGE_LEN)
	p.Write(ELK_EXTENT_ZERO)
	p.Write(ELK_METHOD_STUN)
	p.Write(ELK_OPT_USERNAME)
	d := []byte(name)
	//算用户名字节长度，转换为单字节的整形值，转换为字节
	p.WriteByte(byte(uint8(len(d))))
	p.Write(d)
	p.Write(ELK_OPT_SESSID)
	d = []byte(sessionId)
	p.WriteByte(byte(uint8(len(d))))
	p.Write(d)
	p.WriteByte(0xFF)

	data := p.Bytes()
	//更新包的总长度
	pLen := len(data)
	byteLen := []byte{0x00, 0x00}
	binary.BigEndian.PutUint16(byteLen, uint16(pLen))
	//更新包的总长度
	data[2] = byteLen[0]
	data[3] = byteLen[1]
	fmt.Println("auth data", data)
	return data
}

func isAuth(data []byte) (isAuth bool, size uint8) {
	if 12 != len(data) {
		//认证响应头12个字节
		return false, 0
	}
	size = uint8(data[3])
	isAuth = false
	if 1 == uint8(data[8]) {
		isAuth = true
	}
	return isAuth, size
}

func readFull(conn net.Conn, size uint64) (buffer []byte, err error) {

	buffer = make([]byte, size)
	//缓冲区长度
	SIZE := len(buffer)
	if 0 == SIZE {
		return nil, enerr.New("buffer is not init")
	}
	pos := 0
	//直接定义一个 Buffer 变量，而不用初始化
	for {
		n, err := conn.Read(buffer[pos:])
		if n > 0 {
			//	log.Printf("read len = %d", n)
			pos += n
		}
		if n == 0 {
			time.Sleep(10 * time.Microsecond)
			continue
		}
		if SIZE == pos {
			return buffer, nil
		}
		if nil != err {
			if err == io.EOF {
				continue
			}
			return buffer, err
		}
	}
}

/*
func printCurCookies() {
    var cookieNum int = len(gCurCookies);
    log.Printf("cookieNum=%d", cookieNum)
    for i := 0; i < cookieNum; i++ {
        var curCk *http.Cookie = gCurCookies[i];
        //gLogger.Info("curCk.Raw=%s", curCk.Raw)
        log.Printf("------ Cookie [%d]------", i)
        log.Printf("Name\t=%s", curCk.Name)
        log.Printf("Value\t=%s", curCk.Value)
        log.Printf("Path\t=%s", curCk.Path)
        log.Printf("Domain\t=%s", curCk.Domain)
        log.Printf("Expires\t=%s", curCk.Expires)
        log.Printf("RawExpires=%s", curCk.RawExpires)
        log.Printf("MaxAge\t=%d", curCk.MaxAge)
        log.Printf("Secure\t=%t", curCk.Secure)
        log.Printf("HttpOnly=%t", curCk.HttpOnly)
        log.Printf("Raw\t=%s", curCk.Raw)
        log.Printf("Unparsed=%s", curCk.Unparsed)
    }
}
*/

type MyAuth struct {
	Name       string `json:"name"`
	Password   string `json:"password"`
}

func HeartKeepAlive(conn *tls.Conn) {
	for true {
		time.Sleep(2 * time.Second)
		ELK_VERSION := []byte{0x01}
		ELK_PROTO := []byte{0x01}
		ELK_PACKAGE_LEN := []byte{0x00, 0x00} //len
		ELK_PACKAGE_XID := []byte{0x00, 0x00, 0x00, 0x00}
		ELK_TYPE := []byte{0x03}
		ELK_CODE := []byte{0x00, 0x00, 0x00}
		p := bytes.NewBuffer(ELK_VERSION)
		p.Write(ELK_PROTO)
		p.Write(ELK_PACKAGE_LEN)
		p.Write(ELK_PACKAGE_XID)
		p.Write(ELK_TYPE)
		p.Write(ELK_CODE)
		data := p.Bytes()
		byteLen := []byte{0x00, 0x00}
		binary.BigEndian.PutUint16(byteLen, uint16(12))
		//更新包的总长度
		data[2] = byteLen[0]
		data[3] = byteLen[1]
		_, err := conn.Write(data)
		if nil != err {
			log.Println("[error] Failed to Send heart to server :", err)
            return
		} else {
			//fmt.Println("[server] Send heart data to server:", time.Now())
		}
	}
}
func CheckSum(data []byte) uint16 {
	var (
		sum    uint32
		length int = len(data)
		index  int
	)
	for length > 1 {
		sum += uint32(data[index])<<8 + uint32(data[index+1])
		index += 2
		length -= 2
	}
	if length > 0 {
		sum += uint32(data[index])
	}
	sum += (sum >> 16)

	return uint16(^sum)
}

func GetRandomString(l int) string {
	str := "0123456789abcdefghijklmnopqrstuvwxyz"
	bytes := []byte(str)
	result := []byte{}
	r := rand.New(rand.NewSource(time.Now().UnixNano()))
	for i := 0; i < l; i++ {
		result = append(result, bytes[r.Intn(len(bytes))])
	}
	return string(result)
}

func makeUdpPacket(addr net.IP) []byte {
	var udp UDP

	tmp := []byte(addr)
	udp.Sport = (uint16(tmp[14])<<8 + uint16(tmp[15])) + uint16(20000)
	udp.Dport = 30000

	var buffer bytes.Buffer

	s:= []uint8(GetRandomString(1024))
    udp.Len = uint16(len(s) + 8)

	binary.Write(&buffer, binary.BigEndian, udp)
	binary.Write(&buffer, binary.BigEndian, s)


	udp.Checksum = 0
	//udp.Checksum = CheckSum(buffer.Bytes())
	buffer.Reset()
	binary.Write(&buffer, binary.BigEndian, udp)
	binary.Write(&buffer, binary.BigEndian, s)
	iph := &Header{
		Version:  Version,
		Len:      HeaderLen,
		TOS:      0xc0, // DSCP CS6
		TotalLen: HeaderLen + len(buffer.Bytes()),
		TTL:      100,
		Protocol: 17,
		//Src:      net.IPv4(1, 1, 0, 2),
		Src:      addr,
		Dst:      net.IPv4(192, 168, 100, 180),
	}

	b := iph.Marshal()
	iph.Checksum = int(CheckSum(b))
	c := iph.Marshal()

	data := bytes.NewBuffer(c)
	data.Write(buffer.Bytes())
	return data.Bytes()
}

func makeV6UdpPacket(addr net.IP) []byte {
	var udp UDP

	tmp := []byte(addr)
	udp.Sport = (uint16(tmp[14])<<8 + uint16(tmp[15])) + uint16(20000)
	udp.Dport = 30000

	var buffer bytes.Buffer

	s:= []uint8(GetRandomString(1024))
    udp.Len = uint16(len(s) + 8)

	binary.Write(&buffer, binary.BigEndian, addr)
	binary.Write(&buffer, binary.BigEndian, net.ParseIP("2001::53"))
	binary.Write(&buffer, binary.BigEndian, uint16(17))
	binary.Write(&buffer, binary.BigEndian, uint16(udp.Len))
	binary.Write(&buffer, binary.BigEndian, udp)
	binary.Write(&buffer, binary.BigEndian, s)


	udp.Checksum = CheckSum(buffer.Bytes())
	//udp.Checksum = 0
	buffer.Reset()
	binary.Write(&buffer, binary.BigEndian, udp)
	binary.Write(&buffer, binary.BigEndian, s)
	iph := &V6Header{
        Len:      len(buffer.Bytes()),
		Src:      addr,
		Dst:      net.ParseIP("2001::53"),
	}

	c := iph.Marshal()

	data := bytes.NewBuffer(c)
	data.Write(buffer.Bytes())
	return data.Bytes()
}

func makeIcmpPacket(addr net.IP) ([]byte){
	var icmp  ICMP

	//开始填充数据包
	icmp.Type = 8 //8->echo message  0->reply message
	//icmp.Code = uint8(rand.Intn(255))
	icmp.Code = 0
	icmp.Checksum = 0
	icmp.Identifier = 0
	icmp.SequenceNum = 0

	var (
		buffer bytes.Buffer
	)
	//先在buffer中写入icmp数据报求去校验和
	binary.Write(&buffer, binary.BigEndian, icmp)
	icmp.Checksum = CheckSum(buffer.Bytes())
	//然后清空buffer并把求完校验和的icmp数据报写入其中准备发送
	buffer.Reset()
	binary.Write(&buffer, binary.BigEndian, icmp)

	iph := &Header{
		Version:  Version,
		Len:      HeaderLen,
		TOS:      0xc0, // DSCP CS6
		TotalLen: HeaderLen + len(buffer.Bytes()),
		TTL:      100,
		Protocol: 1,
		//Src:      net.IPv4(1, 1, 0, 2),
		Src:      addr,
		Dst:      net.IPv4(192, 168, 100, 114),
	}

    b := iph.Marshal()
    iph.Checksum = int(CheckSum(b))
    c := iph.Marshal()

    data := bytes.NewBuffer(c)
    data.Write(buffer.Bytes())
	fmt.Println("send ping data", data.Bytes())
    return data.Bytes()

}

func tunnelPingTest(conn *tls.Conn, addr net.IP) {
    for true {
		time.Sleep(10 * time.Millisecond)
        //	ProtoNone   uint32 = 0x00000000 // 协议标识: 未知;
        //	ProtoIPv4   uint32 = 0x00000001 // 协议标识: IPv4;
        //	ProtoIPv6   uint32 = 0x00000002 // 协议标识: IPv6;
        ELK_VERSION := []byte{0x01}
        ELK_PROTO := []byte{0x04}
        //ELK_PROTO := []byte{0x08}
        ELK_PACKAGE_LEN := []byte{0x00, 0x00} //len
        ELK_PACKAGE_XID := []byte{0x00, 0x00, 0x00, 0x00}
        ELK_PACKAGE_APPID := []byte{0x00, 0x00, 0x00, 41} //4字节appid
        /*
        PAYLOAD := []byte{ 0x45, 0x00, 0x00, 0x1e, 0xea, 0xba, 0x00, 0x00, 0x80, 0x01,
                            0x29, 0x8f, 0x01, 0x01, 0x00, 0x02, 0xc0, 0xa8,
                            0x64, 0xea, 0x08, 0x00, 0x96, 0x86, 0x00, 0x01,
                            0x00, 0x16, 0x61, 0x62};
        */

        //PAYLOAD := makeIcmpPacket(addr)
        PAYLOAD := makeUdpPacket(addr)
        //PAYLOAD := makeV6UdpPacket(addr)
        p := bytes.NewBuffer(ELK_VERSION)
        p.Write(ELK_PROTO)
        p.Write(ELK_PACKAGE_LEN)
        p.Write(ELK_PACKAGE_XID)
        p.Write(ELK_PACKAGE_APPID)
        p.Write(PAYLOAD)
        data := p.Bytes()
        byteLen := []byte{0x00, 0x00}
        binary.BigEndian.PutUint16(byteLen, uint16(len(data)))
        //更新包的总长度
        data[2] = byteLen[0]
        data[3] = byteLen[1]
        _, err := conn.Write(data)
        if nil != err {
            log.Println("[server] Failed to Send data to server :", err)
            return
        }
    }
}

func InRecv(conn *tls.Conn) {
	for true {
		header, error := readFull(conn, 8)
		if nil != error {
			log.Println("[server] Failed to read head bytes:", error)
			break
		}
		size := binary.BigEndian.Uint16(header[2:4])
		//size:= uint8(header[3])
		//	log.Print("size:",size)
		if (uint64(size) - 8) > 65535 {
			log.Println("[server] Packet head error:", header[2:4], " size:", size)
			log.Println("[server] Recv head:", header)
			break
		}
		//	fmt.Println("[head]:",header)
		data, err := readFull(conn, uint64(size)-8)
		if nil != err {
			log.Println("[server] Failed to Read server data :", err)
			return
		}
		//	fmt.Println("[body]:",data)
		if header[1] == 2 {
			//fmt.Println("[debug] recv heart from server:", time.Now())
			continue
		}
		//	for _, v := range data {
		//		fmt.Printf("%X ", v)
		//	}

		inbuffer := make([]byte, 0)
		buf := bytes.NewBuffer(inbuffer)
		buf.Write(data)
		if header[1] == 0x08 {
            //fmt.Println("recv data", string(buf.Bytes()[48:]), ", len=", uint64(size)-8)
		} else if header[1] == 0x04 {
            //fmt.Println("recv data", buf.Bytes())
		} else {
			log.Println("[debug] recv unknown  head type:", header[1])
		}
	}
}



func httpPost(user string, pass string, i int) (map[string]interface{}, error) {
    var server string
    server = GatewayHost
	log.Println("[debug] connectTLS server ok ")
	conn, err := connectTLS(server)
	if nil != err {
		fmt.Print("[server] Failed to  Connect to Server :", server, " error info:", err)
        return nil, err
	}

    //token := [2]string{"c9cbdfe2417c87ae82c2d90b68074d3c", "c9cbdfe2417c87ae82c2d90b68074d3d"}
	defer conn.Close()
	log.Println("[debug] connectTLS server ok ")
    //authPackage := auth(strings.Join([]string{user, "1"}, "@"), token[i-1])
    authPackage := auth(strings.Join([]string{user, "1"}, "@"), pass)
	_, err = conn.Write(authPackage)
	if nil != err {
		fmt.Println("[server] Failed to  Send auth data:", authPackage, " error:", err)
        return nil, err
	}
	header, error := readFull(conn, 12)
	if nil != error {
		fmt.Println("[server] Failed to  Read auth data :", error)
        return nil, err
	}
	//log.Println("[debug] read head from server ok ")

	if len(header) == 12 {
		isAuth, size := isAuth(header)
		if isAuth {
			data, err := readFull(conn, uint64(size)-12)
			if nil != err {
				log.Println("[server] Failed to  Read auth data error:", err)
                return nil, err
			}
			//log.Println("[server] Get Server auth data :", data)
			if len(data) < 28 {
				log.Println("[error] server auth data not enough")
                return nil, err
			}
			vInfo := INFO_FROM_REMOTE_SERVER{}

			//TLV
			var Ltype int = 0
			var Postion int = 0
			var Numbers int = 0

			value := int(data[0])
			for {
				if value == 11 {
					for i := 0; i < int(data[Postion+2]); i++ {
						IPv4[i+12] = data[Postion+3+i]
					}
                    tmp := net.IPv4(IPv4[12],IPv4[13], IPv4[14], IPv4[15])
                    go tunnelPingTest(conn, tmp)
					fmt.Println("[debug] Ipv4:", IPv4.To4())
					vInfo.ip = IPv4.String() // strings.Join([]string{strconv.Itoa(int(data[Postion+3])), strconv.Itoa(int(data[Postion+4])), strconv.Itoa(int(data[Postion+5])), strconv.Itoa(int(data[Postion+6]))}, ".")
					Ltype++
					Postion += 3 + int(data[Postion+2])
					value = int(data[Postion])
					//fmt.Println("[debug] ipv4:", vInfo.ip, " position:", Postion)
				} else if value == 12 {
					vInfo.mask = strings.Join([]string{strconv.Itoa(int(data[Postion+3])), strconv.Itoa(int(data[Postion+4])), strconv.Itoa(int(data[Postion+5])), strconv.Itoa(int(data[Postion+6]))}, ".")
					Ltype++
					Postion += 3 + int(data[Postion+2])
					value = int(data[Postion])
					//fmt.Println("[debug] mask:", vInfo.mask, " position:", Postion)
				} else if value == 35 {
					vInfo.gateway = strings.Join([]string{strconv.Itoa(int(data[Postion+3])), strconv.Itoa(int(data[Postion+4])), strconv.Itoa(int(data[Postion+5])), strconv.Itoa(int(data[Postion+6]))}, ".")
					Ltype++
					Postion += 3 + int(data[Postion+2])
					value = int(data[Postion])
					//fmt.Println("[debug] gateway:", vInfo.gateway, " position:", Postion)
				} else if value == 36 {
					len := int(data[Postion+2])
					//fmt.Println("[debug] dns len:", len)
					str := string(data[Postion+3 : Postion+3+len])
					vInfo.dns_ip = str //strings.Join([]string{strconv.Itoa(int(data[Postion+3])), strconv.Itoa(int(data[Postion+4])), strconv.Itoa(int(data[Postion+5])), strconv.Itoa(int(data[Postion+6]))}, ".")
					Ltype++
					Postion += len + 3
					value = int(data[Postion])
					fmt.Println("[debug] dns_ip:", vInfo.dns_ip, " position:", Postion)
				} else if value == 0x35 {
					for i := 0; i < int(data[Postion+2]); i++ {
						IPv6[i] = data[Postion+3+i]
					}
					vInfo.ip_v6 = IPv6.String()
					Ltype++

                    //go tunnelPingTest(conn, IPv6)
					Postion += int(data[Postion+2]) + 3
					value = int(data[Postion])
					fmt.Println("[debug] Ipv6:", vInfo.ip_v6, " position:", Postion)
				} else if value == 0x36 { //dns_ipv6
					for i := 0; i < int(data[Postion+2]); i++ {
						DnsIPv6[i] = data[Postion+3+i]
					}

					vInfo.dns_ipv6 = DnsIPv6.String()
					Ltype++
					Postion += int(data[Postion+2]) + 3
					value = int(data[Postion])
					fmt.Println("[debug] DnsIpv6:", vInfo.dns_ipv6, " position:", Postion)
				} else {
					len := int(data[Postion+2])
					Postion += 3 + len
					//fmt.Println("[debug] other type :", value, " len:", len)
					value = int(data[Postion])
					//fmt.Println("[debug] value:", value)
					if value == 255 {
						break
					}
				}
				Numbers++
				if Ltype == 6 {
					break
				} else if Numbers > 10 {
					log.Println("[error] to more data for check,server auth data error")
                    return nil, err

				}
			}

            go HeartKeepAlive(conn)
            fmt.Println("[debug] aa:", vInfo.ip)
            go InRecv(conn)

            select {}

		} else {
			fmt.Print("[server] Failed to Get server Auth ")
            return nil, nil
		}
	}
	return nil, err
}

func httpPostLogout(gCurCookies []*http.Cookie) {
	client := &http.Client{}
	var req *http.Request
    req, _ = http.NewRequest("POST", "http://192.168.101.209:443/api/enwas/pg/logout", nil)
    var cookieNum int = len(gCurCookies);
    for i := 0; i < cookieNum; i++ {
    var curCk *http.Cookie = gCurCookies[i];
        req.AddCookie(curCk)
    }
    resp, err := client.Do(req)
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		// handle error
		return
	}
	log.Println(string(body))
}

func main() {
    var tunnel_n int
    var speed_n int
    var pool_n int = 1
    flag.IntVar(&tunnel_n, "tunnel_n", 0, "threads")
    flag.IntVar(&pool_n, "pool_n", 1, "vippool count")
    flag.IntVar(&speed_n, "speed_n", 1, "speed")
    flag.StringVar(&GatewayHost, "gatewayhost", "", "gateway ip")

    flag.Parse()

    if len(GatewayHost) <= 0 {
        fmt.Println("GatewayHost is nil")
        os.Exit(0)
    }

    var i int
    i = 0
    interval := time.Duration(1000000/speed_n)

    cleanupDone := make(chan bool)

    for cc:= 0; cc < tunnel_n; cc++ {
        str := "test" + strconv.Itoa(i)
        md5Str := "pool-" + strconv.Itoa(i%pool_n + 1) + "-" + md5V2(str)
        i = i + 1
        fmt.Println("pass ", md5Str, "", str)
        go httpPost(str,md5Str,i)

        time.Sleep(interval * time.Microsecond)
    }

    <-cleanupDone
}
