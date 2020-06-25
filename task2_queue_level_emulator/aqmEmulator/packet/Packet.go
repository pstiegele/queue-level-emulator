package packet

type Packet struct {
	data []byte
	size int
	enqueueTimestamp int
	dequeueTimestamp int
	//to be continued
}

func Create(data []byte)  {
	//return Packet{data:data}
}