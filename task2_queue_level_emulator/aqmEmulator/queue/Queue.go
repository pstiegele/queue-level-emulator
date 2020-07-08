package queue

import (
	"aqmEmulator/packet"
	"time"
	// "os"
	// "encoding/json"
	// "strconv"
	// "bytes"
	//"log"
)

//todo: add synchronization because of threads
//todo: add clarification to size (is it packet or byte size?)

type Queue struct{
	maxSize int
	size *int
	data []packet.Packet
}

func NewQueue(maxSize int, currentQueueSize *int) *Queue{
	q := Queue{maxSize: maxSize, size: currentQueueSize}
	q.data = make([]packet.Packet, 0, maxSize)
	return &q
}

func (q *Queue) Push(packet *packet.Packet) bool {
	if(*q.size+1>q.maxSize){
		return false
	}
	packet.EnqueueTimestamp = time.Now().UnixNano()
	q.data = append(q.data, *packet)
	*q.size += 1
	//log.Println("package enqueued")
	//Todo: return correct result
	// go func(q *Queue){
	// 	arr := make([]string, 0, 1000000)
	// 	for _, element := range q.data {
	// 			out, _ := json.Marshal(element)
	// 			arr = append(arr, string(out))
	// 	}
	// 	//log.Println(arr)
	// 	var buffer bytes.Buffer
	// 	for _, arrelement := range arr {
	// 		buffer.WriteString(arrelement+"\n\n")
	// 	}
	// 	if(len(arr)!=0){
	// 		f, _ := os.Create("/home/pstiegele/log/"+strconv.Itoa(int(time.Now().UnixNano())))
	// 	defer f.Close()
	// 	f.WriteString(buffer.String())
	// 	f.Sync()
	// 	}
	// }(q)
	
	
	return true
}

//returns actual packet size in bytes
func (q *Queue) NextPacketSize() int {
	if len(q.data) == 0 {
		return 0
	}
	size := q.data[0].Size
	//log.Println(*q.size)
	if(size == 0){
		q.Pop()
	}
	return size
}

func (q *Queue) Pop() *packet.Packet {
	if len(q.data) == 0 {
		return nil
	}
	p := q.data[0]
	*q.size -= 1
	p.DequeueTimestamp = time.Now().UnixNano()
	//log.Println(*q.size)
	q.data = q.data[1:]
	//log.Println("package dequeued")
	return &p
}