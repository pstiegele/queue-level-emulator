package scheduler

import (
	"time"
	"sync"
	//"log"
	"aqmEmulator/queue"
	"aqmEmulator/aqm"
	"aqmEmulator/sender"
)

//this scheduler uses the Tokenbucket algorithm
func NewScheduler(wg *sync.WaitGroup, queue *queue.Queue, sender *sender.Sender, aqm *aqm.Aqm, bucket *int64, maxBucketSize int64) {
	//todo: parameter auslagern
	//todo: time sleep einfügen und auslagern
	var tokenGenerationRate int64 = 100
	*bucket = maxBucketSize
	var lastTokenUpdate int64 = time.Now().UnixNano()

	for {
		now := time.Now().UnixNano()
		deltaT :=  now - lastTokenUpdate
		lastTokenUpdate = now
		newTokens := deltaT * tokenGenerationRate
		if(*bucket + newTokens > maxBucketSize){
			*bucket = maxBucketSize
		}else{
			*bucket+=newTokens
		}

		var nextPacketSize int64 = int64(queue.NextPacketSize())
		if(nextPacketSize != 0 && nextPacketSize < *bucket){
			//log.Println("scheduler takes packet out of queue")
			p := queue.Pop()
			if p != nil{
				if(aqm.SendingOk(p)){
					//log.Println("aqm says its ok to send, so transport the packet to the sender")
					sender.Send(p)
				}
				
			}
		}
		time.Sleep(1 * time.Millisecond)
	}

	defer wg.Done()
}