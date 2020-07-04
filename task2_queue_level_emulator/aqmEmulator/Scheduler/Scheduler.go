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
func NewScheduler(wg *sync.WaitGroup, m sync.Mutex, queue *queue.Queue, sender *sender.Sender, aqm *aqm.Aqm, bucket *int64, maxBucketSize int64) {
	//todo: parameter auslagern
	//todo: time sleep einfügen und auslagern
	tokenGenerationRate := 0.001
	*bucket = maxBucketSize
	var lastTokenUpdate int64 = time.Now().UnixNano()

	for {
		now := time.Now().UnixNano()
		deltaT :=  now - lastTokenUpdate
		//log.Printf("deltaT: %d", deltaT)
		lastTokenUpdate = now
		newTokens := int64(float64(deltaT) * tokenGenerationRate)
		//log.Printf("newTokens: %d", newTokens)
		if(*bucket + newTokens > maxBucketSize){
			*bucket = maxBucketSize
		}else{
			*bucket+=newTokens
		}
		//log.Printf("bucket size: %d", *bucket)
		m.Lock()
		var nextPacketSize int64 = int64(queue.NextPacketSize())
		m.Unlock()
		//log.Printf("next packet size: %d", nextPacketSize)
		
		if(nextPacketSize != 0 && nextPacketSize < *bucket){
			//log.Println("scheduler takes packet out of queue")
			m.Lock()
			p := queue.Pop()
			m.Unlock()
			if p != nil{
				if(aqm.SendingOk(p)){
					//log.Println("aqm says its ok to send, so transport the packet to the sender")
					sender.Send(p)
				}
				
			}
		}
		//time.Sleep(10 * time.Nanosecond)
	}

	defer wg.Done()
}