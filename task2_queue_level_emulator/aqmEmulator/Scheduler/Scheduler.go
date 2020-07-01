package scheduler

import (
	//"time"
	"sync"
	//"log"
	"aqmEmulator/queue"
	"aqmEmulator/sender"
)

func NewScheduler(wg *sync.WaitGroup, queue *queue.Queue, sender *sender.Sender ) {
	for {
		p := queue.Pop()
		if p != nil{
			//log.Println("packet popped by scheduler")
			sender.Send(p)
		}
		
		//time.Sleep(1 * time.Millisecond)
	}

	defer wg.Done()
}