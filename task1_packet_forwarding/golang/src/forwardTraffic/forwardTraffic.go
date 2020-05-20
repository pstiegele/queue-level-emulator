package main

import (
	"bytes"
	"fmt"
	"log"
	"net"
	"syscall"
	"time"
)

func main() {
	fmt.Printf("started!\n")
	go receive("h2-eth0", []byte{0, 0, 0, 0, 0, 1}, []byte{0, 0, 0, 0, 0, 3}, "h2-eth1", 1)
	go receive("h2-eth1", []byte{0, 0, 0, 0, 0, 3}, []byte{0, 0, 0, 0, 0, 1}, "h2-eth0", 1)
	time.Sleep(60 * time.Second)
}

func receive(receiveInterface string, srcMac []byte, destMac []byte, sendingInterface string, turnSendingOn int){
	fd, _ := syscall.Socket(syscall.AF_PACKET, syscall.SOCK_RAW, 0x0300)
	//err := syscall.BindToDevice(fd, receiveInterface)
	//err := syscall.SetsockoptString(fd, syscall.SOL_SOCKET, syscall.SO_BINDTODEVICE, receiveInterface)
	iface, _ := net.InterfaceByName(receiveInterface)
	sa := syscall.SockaddrLinklayer{
		Ifindex:  iface.Index,
	}
	syscall.Bind(fd, &sa)
	//f := os.NewFile(uintptr(fd), fmt.Sprintf("fd %d", fd))
	//if err != nil {
	//	syscall.Close(fd)
	//	panic(err)
	//}
	for {
		buf := make([]byte, 1518)
		n, _, _ := syscall.Recvfrom(fd, buf, 0)
		dest := buf[0:6]
		src := buf[6:12]
		if !bytes.Equal(dest, []byte{0, 0, 0, 0, 0, 0}){
			//fmt.Println("receivingInterface: ", receiveInterface, " | src:", src, " | destination:", dest, ": ")
			//fmt.Println(buf[:n])
		}

		if bytes.Equal(src, srcMac){
			if bytes.Equal(dest, destMac) || bytes.Equal(dest, []byte{255, 255, 255, 255, 255, 255}) { //broadcast address changed to 254
				//fmt.Println("sending from ", src, " to ", dest)
				send(buf[:n], sendingInterface)
			}
		}

	}
}



func send(p []byte, sendingInterface string){
	fd, _ := syscall.Socket(syscall.AF_PACKET, syscall.SOCK_RAW, 0x0300)
	//err := syscall.BindToDevice(fd, "h2-eth1")
	//if err != nil {
	//	syscall.Close(fd)
	//	panic(err)
	//}
	iface, err := net.InterfaceByName(sendingInterface)
	sa := &syscall.SockaddrLinklayer{Ifindex: iface.Index}

	if err != nil {
		log.Fatal("sendingInterface: ", sendingInterface, " | Sendto:", err)
	}

	err = syscall.Sendto(fd, p, 0, sa)
	if err != nil {
		log.Fatal("sendingInterface: ", sendingInterface, " | Sendto:", err)
	}
}
