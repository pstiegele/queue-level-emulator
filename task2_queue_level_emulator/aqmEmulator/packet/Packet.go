package packet

type Packet struct {
	Data []byte
	size int
	enqueueTimestamp int
	dequeueTimestamp int
	//to be continued
}

func NewPacket(data []byte) *Packet  {
	p := Packet{Data: data}
	return &p
}