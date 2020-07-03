package sender

import (
	"syscall"
	"net"
	"log"
	"os"
	"aqmEmulator/packet"
)

type Sender struct {
	fd_sending int
	sentPackets *int 
	sa_sending *syscall.SockaddrLinklayer
}

func NewSender(senderInterface string, sentPackets *int)  *Sender {
	//create sending interface 
	fd_sending, _ := syscall.Socket(syscall.AF_PACKET, syscall.SOCK_RAW, 0x0300)
	iface_sending, _ := net.InterfaceByName(senderInterface)
	if iface_sending == nil{
		log.Fatal("Sending interface not found: "+senderInterface)
		os.Exit(3)
	}
	sa_sending := &syscall.SockaddrLinklayer{Ifindex: iface_sending.Index}

	return &Sender{fd_sending: fd_sending, sa_sending: sa_sending, sentPackets: sentPackets}
}



func (s *Sender) Send(p *packet.Packet){
	//log.Println("packet sent by sender")
	syscall.Sendto(s.fd_sending, p.Data, 0, s.sa_sending)
	*s.sentPackets++;
}