package queue

import (
	"aqmEmulator/packet"
	"time"
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
	//Todo: check if queue is full
	//Todo: what to do with Queue.size?
	if(*q.size+1>q.maxSize){
		return false
	}
	packet.EnqueueTimestamp = time.Now().UnixNano()
	q.data = append(q.data, *packet)
	*q.size += 1
	//log.Println("package enqueued")
	//Todo: return correct result
	return true
}

//actual packet size in bytes
func (q *Queue) NextPacketSize() int {
	if len(q.data) == 0 {
		return 0
	}
	size := q.data[0].Size
	return size
}

func (q *Queue) Pop() *packet.Packet {
	if len(q.data) == 0 {
		return nil
	}
	p := q.data[0]
	*q.size -= 1
	p.DequeueTimestamp = time.Now().UnixNano()
	q.data = q.data[1:]
	//log.Println("package dequeued")
	return &p
}