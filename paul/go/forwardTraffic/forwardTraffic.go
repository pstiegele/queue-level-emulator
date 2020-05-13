package main

import (
	"bytes"
	"fmt"
	"log"
	"net"
	"os"
	"syscall"
)

func main() {
	receive_layer2()
}


func receive_layer2(){
	fd, _ := syscall.Socket(syscall.AF_INET, syscall.SOCK_RAW, syscall.IPPROTO_ICMP) //IPPROTO_RAW?
	f := os.NewFile(uintptr(fd), fmt.Sprintf("fd %d", fd))

	for {
		buf := make([]byte, 1024)
		numRead, err := f.Read(buf)
		if err != nil {
			fmt.Println(err)
		}
		src := buf[12:16]
		dest := buf[16:20]
		fmt.Print("src:", src, " | destination:", dest, ": ")
		fmt.Printf("% X\n", buf[:numRead])
		if bytes.Equal(dest, []byte{10, 0, 1, 1}) || bytes.Equal(dest, []byte{10, 0, 3, 1}){
			send_layer2(buf[:numRead], dest)
		}

	}
}


func send_layer2(p []byte, dest []byte){
	var err error
	fd, _ := syscall.Socket(syscall.AF_INET, syscall.SOCK_RAW, syscall.IPPROTO_RAW)
	p[8] = p[8]-1 //reduce ttl?
	if p[8]<=0{ //if ttl <=0, forget the packet
		return
	}
	var a [4]byte
	copy(a[:], dest[:4])
	addr := syscall.SockaddrInet4{
		Port: 0,
		Addr: a,
	}
	//p := pkt()
	err = syscall.Sendto(fd, p, 0, &addr)
	if err != nil {
		log.Fatal("Sendto:", err)
	}
}

//func pkt() []byte {
//	h := Header{
//		Version:  4,
//		Len:      20,
//		TotalLen: 20 + 10, // 20 bytes for IP, 10 for ICMP
//		TTL:      64,
//		Protocol: 1, // ICMP
//		Dst:      net.IPv4(127, 0, 0, 1),
//		// ID, Src and Checksum will be set for us by the kernel
//	}
//
//	icmp := []byte{
//		8, // type: echo request
//		0, // code: not used by echo request
//		0, // checksum (16 bit), we fill in below
//		0,
//		0, // identifier (16 bit). zero allowed.
//		0,
//		0, // sequence number (16 bit). zero allowed.
//		0,
//		0xC0, // Optional data. ping puts time packet sent here
//		0xDE,
//	}
//	cs := csum(icmp)
//	icmp[2] = byte(cs)
//	icmp[3] = byte(cs >> 8)
//
//	out, err := h.Marshal()
//	if err != nil {
//		log.Fatal(err)
//	}
//	return append(out, icmp...)
//}
//
//func csum(b []byte) uint16 {
//	var s uint32
//	for i := 0; i < len(b); i += 2 {
//		s += uint32(b[i+1])<<8 | uint32(b[i])
//	}
//	// add back the carry
//	s = s>>16 + s&0xffff
//	s = s + s>>16
//	return uint16(^s)
//}



func receive_layer3(){
	protocol := "icmp"
	//netaddr, _ := net.ResolveIPAddr("ip4", "127.0.0.1")
	conn, _ := net.ListenIP("ip4:"+protocol, nil)

	for {
		buf := make([]byte, 1024)
		numRead, _, _ := conn.ReadFrom(buf)
		fmt.Printf("% X\n", buf[:numRead])
		destination_address := buf[32:35] //falsch
		fmt.Println("destination", destination_address)
		send_layer3(buf[:numRead])
	}

}


func send_layer3(p []byte){
	conn, err := net.Dial("ip4:icmp", "10.0.3.1")
	if err != nil {
		log.Fatalf("Dial: %s\n", err)
	}

	conn.Write(p)
}