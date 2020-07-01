package receiver

import (
	"log"
	"syscall"
	"net"
	"sync"
	"bytes"
	"aqmEmulator/queue"
	"aqmEmulator/packet"
)

type ForwardingRules struct {
	Src []byte
	Dest []byte
}

func NewReceiver(wg *sync.WaitGroup, receiverInterface string, queue *queue.Queue, fr ForwardingRules ) {
	fd, err := syscall.Socket(syscall.AF_PACKET, syscall.SOCK_RAW, 0x0300)
	iface, _ := net.InterfaceByName(receiverInterface)
	sa := syscall.SockaddrLinklayer{
		Ifindex:  iface.Index,
	}

	if err != nil {
		log.Fatal("receive error occured: ", err)
	}



	syscall.Bind(fd, &sa)

	for {
		buf := make([]byte, 4096)
		n, _, _ := syscall.Recvfrom(fd, buf, 0)
		dest := buf[0:6]
		src := buf[6:12]
		
		//create packet here
		//log.Println(buf[:n])
		p := packet.NewPacket(buf[:n])
		_, _, _, _ = buf, n, dest, src
		//put packet here into the queue
		if(needsforwarding(p, fr)){
			//log.Println("packet received --> needsForwarding")
			queue.Push(p)
		}else{
			//log.Println("packet received --> dropped")
		}
		

	}

	defer wg.Done()
}


func needsforwarding(p *packet.Packet, fr ForwardingRules) bool{
	if(bytes.Equal(p.Src, fr.Src) && (bytes.Equal(p.Dest, fr.Dest) || bytes.Equal(p.Dest, []byte{255, 255, 255, 255, 255, 255}))){
		return true
	}
	return false
}