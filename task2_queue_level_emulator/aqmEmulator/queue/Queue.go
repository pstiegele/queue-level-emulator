package queue

import (
	"aqmEmulator/packet"
)


type Queue struct{
	size int
	data []packet.Packet
}

func NewQueue(size int) *Queue{
	q := Queue{size: size}
	q.data = make([]packet.Packet, 0, size)
	return &q
}

func (q *Queue) Push(packet *packet.Packet) bool {
	//Todo: check if queue is full
	//Todo: check if aqm allows push
	//Todo: what to do with Queue.size?
	q.data = append(q.data, *packet)
	//Todo: return correct result
	return true
}

func (q *Queue) Pop() *packet.Packet {
	if len(q.data) == 0 {
		return nil
	}
	p := q.data[0]
	q.data = q.data[1:]
	return &p
}