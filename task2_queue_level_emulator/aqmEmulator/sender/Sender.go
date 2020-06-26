package sender

import (
	"syscall"
	"net"
	"aqmEmulator/packet"
)

type Sender struct {
	fd_sending int
	sa_sending *syscall.SockaddrLinklayer
}

func NewSender(senderInterface string)  Sender {
	//create sending interface 
	fd_sending, _ := syscall.Socket(syscall.AF_PACKET, syscall.SOCK_RAW, 0x0300)
	iface_sending, _ := net.InterfaceByName(senderInterface)
	sa_sending := &syscall.SockaddrLinklayer{Ifindex: iface_sending.Index}

	return Sender{fd_sending: fd_sending, sa_sending: sa_sending}
}



func (s *Sender) Send(p *packet.Packet){
	syscall.Sendto(s.fd_sending, p.Data, 0, s.sa_sending)
}