package packet

type Packet struct {
	Data []byte
	size int
	enqueueTimestamp int
	dequeueTimestamp int
	Src []byte
	Dest []byte
	//to be continued
}

func NewPacket(data []byte) *Packet  {
	p := Packet{Data: data, Dest: data[0:6], Src: data[6:12]}
	return &p
}