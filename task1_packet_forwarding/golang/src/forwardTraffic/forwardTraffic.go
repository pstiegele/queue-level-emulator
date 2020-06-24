package main

import (
	"bytes"
	"fmt"
	"log"
	"net"
	"syscall"
	"sync"
)

func main() {
	//fmt.Printf("golang package forwarding started!\n")
	wg := new(sync.WaitGroup)
	go receive("h2-eth0", []byte{0, 0, 0, 0, 0, 1}, []byte{0, 0, 0, 0, 0, 3}, "h2-eth1", 1, wg)
	go receive("h2-eth1", []byte{0, 0, 0, 0, 0, 3}, []byte{0, 0, 0, 0, 0, 1}, "h2-eth0", 1, wg)
	wg.Add(2)
	wg.Wait()
}

func receive(receiveInterface string, srcMac []byte, destMac []byte, sendingInterface string, turnSendingOn int, wg *sync.WaitGroup){
	fd, err := syscall.Socket(syscall.AF_PACKET, syscall.SOCK_RAW, 0x0300)
	iface, _ := net.InterfaceByName(receiveInterface)
	sa := syscall.SockaddrLinklayer{
		Ifindex:  iface.Index,
	}

	//create sending interface 
	fd_sending, _ := syscall.Socket(syscall.AF_PACKET, syscall.SOCK_RAW, 0x0300)
	iface_sending, _ := net.InterfaceByName(sendingInterface)
	sa_sending := &syscall.SockaddrLinklayer{Ifindex: iface_sending.Index}

	if err != nil {
		log.Fatal("sendingInterface: ", sendingInterface, " | Sendto:", err)
	}


	syscall.Bind(fd, &sa)
	for {
		buf := make([]byte, 4096)
		n, _, _ := syscall.Recvfrom(fd, buf, 0)
		dest := buf[0:6]
		src := buf[6:12]
		//if !bytes.Equal(dest, []byte{0, 0, 0, 0, 0, 0}){
			//fmt.Println("receivingInterface: ", receiveInterface, " | src:", src, " | destination:", dest, ": ")
			//fmt.Println(buf[:n])
		//}

		if bytes.Equal(src, srcMac){
			if bytes.Equal(dest, destMac) || bytes.Equal(dest, []byte{255, 255, 255, 255, 255, 255}) { 
				//fmt.Println("sending from ", src, " to ", dest)
				syscall.Sendto(fd_sending, buf[:n], 0, sa_sending)
			}
		}

	}
	defer wg.Done()
}