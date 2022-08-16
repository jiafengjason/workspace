package main

/*
#cgo CFLAGS: -I include
#cgo LDFLAGS: -L lib -Wl,-rpath=lib -lclient -lfko -lnetfilter_queue
#include "fko.h"
#include "client.h"
#include "netfilter.h"
#include <string.h>
#include <stdlib.h>
*/
import "C"
import (
	"encoding/hex"
	"errors"
	"fmt"
	"log"
	"sync"
	"time"
	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
	"net"
	"strconv"
	"unsafe"
)

var (
	udpToken string = "ffcbbd5d0ff16b8d161b80a8be26b918"
	tcpToken string= "enlink"
)

type NFQueue struct {
	h       *C.struct_nfq_handle
	qh      *C.struct_nfq_q_handle
	fd      C.int
	packets chan NFPacket
	idx     uint32
}

type NFPacket struct {
	Packet gopacket.Packet
	qh     *C.struct_nfq_q_handle
	id     C.uint32_t
}

const (
	AF_INET  = 2
	AF_INET6 = 10

	NF_DROP   Verdict = 0
	NF_ACCEPT Verdict = 1
	NF_STOLEN Verdict = 2
	NF_QUEUE  Verdict = 3
	NF_REPEAT Verdict = 4
	NF_STOP   Verdict = 5

	NF_DEFAULT_PACKET_SIZE uint32 = 0xffff

	ipv4version = 0x40
)

type Verdict C.uint
var theTable = make(map[uint32]*chan NFPacket, 0)
var theTabeLock sync.RWMutex

func udpSpa(ip net.IP, DstPort int, spaPort int) (error) {
	//udp 敲门
	var ctx C.fko_ctx_t
	var spa_data *C.char
	res := C.fko_new(&ctx)
	if res != C.FKO_SUCCESS {
		C.fko_destroy(ctx)
	    return errors.New("[spa] fko ctx new failed")
	}
	res = C.fko_set_spa_message_type(ctx, C.FKO_ACCESS_MSG)
	if res != C.FKO_SUCCESS {
		C.fko_destroy(ctx)
		return errors.New("[spa] fko ctx set message type failed")
	}

	info := ip.String() + ",tcp/" + strconv.Itoa(DstPort)
	cinfo := C.CString(info)
	defer C.free(unsafe.Pointer(cinfo))

	res = C.fko_set_spa_message(ctx, cinfo)
	if res != C.FKO_SUCCESS {
		C.fko_destroy(ctx)
		return errors.New("[spa] fko ctx set message failed")
	}
	udpspaKey, _ := hex.DecodeString(udpToken)
	res = C.fko_enlink_spa_data_final(ctx, (*C.uchar)(unsafe.Pointer(&udpspaKey[0])), C.FKO_HMAC_MD5)
	if res != C.FKO_SUCCESS {
		C.fko_destroy(ctx)
		return errors.New("[spa] fko ctx set enlink spa data final failed")
	}
	res = C.fko_get_spa_data(ctx, &spa_data)
	if res != C.FKO_SUCCESS {

		C.fko_destroy(ctx)
		return errors.New("[spa] fko ctx get spa data failed")
	}
	size := C.strlen(spa_data)
	data := C.GoBytes(unsafe.Pointer(spa_data), (C.int(size)))
	C.fko_destroy(ctx)

	//udp发送udp spa data
	rAddr := &net.UDPAddr{IP: ip, Port: spaPort}
	lAddr := &net.UDPAddr{IP: net.IPv4zero, Port: 0}
	conn, err := net.DialUDP("udp", lAddr, rAddr)
	if err != nil {
		return errors.New("[spa] udp send spa packet failed")
	}
	conn.Write(data)
	conn.Close()
	return  nil
}

func tcpSpa()  {
	nfq, err := newNFQueue(0, 100, NF_DEFAULT_PACKET_SIZE)
	if err != nil {
		log.Println("init netfilter nfque failed", err)
		return
	}

	log.Println("Start listen sync packets, tcp spa start")
	defer nfq.Close()
	packets := nfq.GetPackets()

	for true {
		select {
		case p := <-packets:
			go func(packet NFPacket) {
				var send = false
				tcpLayer := p.Packet.Layer(layers.LayerTypeTCP)
				ipLayer := p.Packet.Layer(layers.LayerTypeIPv4)
				if tcpLayer != nil && ipLayer != nil {
					tcp, _ := tcpLayer.(*layers.TCP)
					ip, _ := ipLayer.(*layers.IPv4)
					if tcp.SYN == true {
						if SpaMethod != "udp" {
							data := make([]byte, 8)
							pass := []byte(tcpToken)
							length := len(pass)
							spaRefreshTime := SpaRefreshTime
							C.generateOption((*C.char)(unsafe.Pointer(&(pass[0]))), C.int(length), C.uint(tcp.Seq),
								C.uint(spaRefreshTime), (*C.char)(unsafe.Pointer(&data[0])))
							//添加敲门option
							tcpoption := layers.TCPOption{
								OptionType:   101,
								OptionLength: 10,
								OptionData:   data,
							}
							tcp.Options = append(tcp.Options, tcpoption)
							tcp.SetNetworkLayerForChecksum(ip)

							buf := gopacket.NewSerializeBuffer()
							opts := gopacket.SerializeOptions{
								FixLengths:       true,
								ComputeChecksums: true,
							}
							err := gopacket.SerializeLayers(buf, opts, ip, tcp)
							if err == nil {
								send = true
								log.Println("[tcpspa] set tcp option header")
								p.SetVerdictWithPacket(NF_ACCEPT, buf.Bytes())
							}
						}
					}
				}
				if send == false {
					p.SetVerdict(NF_ACCEPT)
				}
			}(p)
		}


	}
}

func spaInit(ip string)  {
	if SpaMethod == "udp" {
		return
	}
	iptablesNewChain("filter","OUTPUT","tcp_spa")
	iptablesClearChain("filter", "tcp_spa")
	iptablesAppendUnique("filter", "tcp_spa", "-p", "tcp", "--syn", "-m", "state", "--state", "NEW", "!", "-s", ip, "-d", ip, "-j", "NFQUEUE", "--queue-num", "0")
	go tcpSpa()
}

func newNFQueue(queueId uint16, maxPacketsInQueue uint32, packetSize uint32) (*NFQueue, error) {
	var nfq = NFQueue{}
	var err error
	var ret C.int

	if nfq.h, err = C.nfq_open(); err != nil {
		return nil, fmt.Errorf("Error opening NFQueue handle: %v\n", err)
	}

	if ret, err = C.nfq_unbind_pf(nfq.h, AF_INET); err != nil || ret < 0 {
		return nil, fmt.Errorf("Error unbinding existing NFQ handler from AF_INET protocol family: %v\n", err)
	}

	if ret, err = C.nfq_unbind_pf(nfq.h, AF_INET6); err != nil || ret < 0 {
		return nil, fmt.Errorf("Error unbinding existing NFQ handler from AF_INET6 protocol family: %v\n", err)
	}

	if ret, err := C.nfq_bind_pf(nfq.h, AF_INET); err != nil || ret < 0 {
		return nil, fmt.Errorf("Error binding to AF_INET protocol family: %v\n", err)
	}

	if ret, err := C.nfq_bind_pf(nfq.h, AF_INET6); err != nil || ret < 0 {
		return nil, fmt.Errorf("Error binding to AF_INET6 protocol family: %v\n", err)
	}

	nfq.packets = make(chan NFPacket,1000)
	nfq.idx = uint32(time.Now().UnixNano())
	theTabeLock.Lock()
	theTable[nfq.idx] = &nfq.packets
	theTabeLock.Unlock()
	if nfq.qh, err = C.CreateQueue(nfq.h, C.u_int16_t(queueId), C.u_int32_t(nfq.idx)); err != nil || nfq.qh == nil {
		C.nfq_close(nfq.h)
		return nil, fmt.Errorf("Error binding to queue: %v\n", err)
	}

	if ret, err = C.nfq_set_queue_maxlen(nfq.qh, C.u_int32_t(maxPacketsInQueue)); err != nil || ret < 0 {
		C.nfq_destroy_queue(nfq.qh)
		C.nfq_close(nfq.h)
		return nil, fmt.Errorf("Unable to set max packets in queue: %v\n", err)
	}

	if C.nfq_set_mode(nfq.qh, C.u_int8_t(2), C.uint(packetSize)) < 0 {
		C.nfq_destroy_queue(nfq.qh)
		C.nfq_close(nfq.h)
		return nil, fmt.Errorf("Unable to set packets copy mode: %v\n", err)
	}

	if nfq.fd, err = C.nfq_fd(nfq.h); err != nil {
		C.nfq_destroy_queue(nfq.qh)
		C.nfq_close(nfq.h)
		return nil, fmt.Errorf("Unable to get queue file-descriptor. %v\n", err)
	}

	go nfq.run()

	return &nfq, nil
}

//Unbind and close the queue
func (nfq *NFQueue) Close() {
	C.nfq_destroy_queue(nfq.qh)
	C.nfq_close(nfq.h)
	theTabeLock.Lock()
	close(nfq.packets)
	delete(theTable, nfq.idx)
	theTabeLock.Unlock()
}

//Get the channel for packets
func (nfq *NFQueue) GetPackets() <-chan NFPacket {
	return nfq.packets
}

func (nfq *NFQueue) run() {
	if errno := C.Run(nfq.h, nfq.fd); errno != 0 {
		log.Println("Terminating, unable to receive packet due to errno=", errno)
	}
}

//export go_callback
func go_callback(packetId C.uint32_t, data *C.uchar, length C.int, idx uint32, qh *C.struct_nfq_q_handle) {
	xdata := C.GoBytes(unsafe.Pointer(data), length)

	var packet gopacket.Packet
	if xdata[0]&0xf0 == ipv4version {
		packet = gopacket.NewPacket(xdata, layers.LayerTypeIPv4, gopacket.DecodeOptions{Lazy: true, NoCopy: true})
	} else {
		packet = gopacket.NewPacket(xdata, layers.LayerTypeIPv6, gopacket.DecodeOptions{Lazy: true, NoCopy: true})
	}

	p := NFPacket{
		Packet: packet,
		qh:     qh,
		id:     packetId,
	}

	theTabeLock.RLock()
	cb, ok := theTable[idx]
	theTabeLock.RUnlock()
	if !ok {
		log.Println("Dropping, unexpectedly due to bad idx=", idx)
		p.SetVerdict(NF_DROP)
	}

	// Nonblocking write of packet to queue channel
	select {
	case *cb <- p:
	default:
		log.Println("Dropping, unexpectedly due to no recv, idx=", idx)
		p.SetVerdict(NF_DROP)
	}
}
//Set the verdict for the packet
func (p *NFPacket) SetVerdict(v Verdict) {
	C.nfq_set_verdict(p.qh, p.id, C.uint(v), 0, nil)
}

//Set the verdict for the packet (in the case of requeue)
func (p *NFPacket) SetRequeueVerdict(newQueueId uint16) {
	v := uint(NF_QUEUE)
	q := (uint(newQueueId) << 16)
	v = v | q
	C.nfq_set_verdict(p.qh, p.id, C.uint(v), 0, nil)
}

//Set the verdict for the packet AND provide new packet content for injection
func (p *NFPacket) SetVerdictWithPacket(v Verdict, packet []byte) {
	C.nfq_set_verdict(
		p.qh,
		p.id,
		C.uint(v),
		C.uint(len(packet)),
		(*C.uchar)(unsafe.Pointer(&packet[0])),
	)
}