package packet

import(
	//"log"
)

type Packet struct {
	Data []byte
	Size int
	EnqueueTimestamp int64
	DequeueTimestamp int64
	Src []byte
	Dest []byte
}

func NewPacket(data []byte) *Packet  {
	p := Packet{Data: data, Dest: data[0:6], Src: data[6:12], Size: len(data)}
	//if(p.Size == 0){
		//log.Println(p)
	//}
	
	return &p
}