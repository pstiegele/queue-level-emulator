package receiver

import (
	"log"
	"syscall"
	"net"
	"sync"
	"aqmEmulator/queue"
	"aqmEmulator/packet"
)

func NewReceiver(wg *sync.WaitGroup, receiverInterface string, queue *queue.Queue ) {
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
		p := packet.NewPacket(buf[:n])
		_, _, _, _ = buf, n, dest, src
		//put packet here into the queue
		queue.Push(p)

	}

	defer wg.Done()
}