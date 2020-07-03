package aqm

import(
	"time"
	"math"
	//"log"
	"aqmEmulator/packet"
)


type Aqm struct{
	interval int64
	target int64
	nextDropTime int64
	droppedCount *float64
	currentAverageDeltaT *float64
	packetsDropped *int
}

func NewAqm(interval int64, target int64, droppedCount *float64, currentAverageDeltaT *float64, packetsDropped *int) *Aqm{
	return &Aqm{interval: interval, target: target, nextDropTime: 0, droppedCount: droppedCount, currentAverageDeltaT: currentAverageDeltaT, packetsDropped: packetsDropped}
}

//note: dropping will take place at the end of each period if the delay is over 5ms ( so last packet of each period)
//https://www-res.cablelabs.com/wp-content/uploads/2019/02/28094033/Active_Queue_Management_Algorithms_DOCSIS_3_0.pdf


//local_minDelay = 0  //If loca_minDelay > target, then drop() head of queue and set_nextDropTimle


/*
 set the enqueue-timestamp of packet
*/
//func enqueue
//	packet.setEnqueueTimestampe()

/*
Two scenarios will happend : dequeuing successfully OR drop()
1. conditon for successfully dequeing:	local_min < target OR now < next_Drop_time (even though delay > target, but when next_drop_interval has not arrived yet, we still forward packet)
2. conditon for dropping: local_min > target AND now < next_Drop_time

function will RETURN:
	TRUE if dequeue sucessfully
	FALSE if there is a drop
*/	
func (aqm *Aqm) SendingOk(p *packet.Packet) bool{
	// log.Println("dequeueTimestamp: ")
	// log.Println(p.DequeueTimestamp)
	// log.Println("enqueueTimestamp: ")
	// log.Println(p.EnqueueTimestamp)
	// log.Println("target: ")
	// log.Println(aqm.target)
	// log.Println("nextDropTime: ")
	// log.Println(aqm.nextDropTime)
	deltaT := p.DequeueTimestamp-p.EnqueueTimestamp
	*aqm.currentAverageDeltaT = float64(*aqm.currentAverageDeltaT)*0.95+float64(deltaT)*0.05
	if (deltaT > aqm.target){
		if (time.Now().UnixNano() < aqm.nextDropTime){
			//forward_packet();
			return true
		}else{
			//drop()
			setNextDropTime(aqm)  //if no packet has delay below target in 100ms, then this line is executed.
			return false
		}
	}else{
		resetNextDropTime(aqm);  //if one packet delay ever falls under target, then reset to 100ms 
		//forward_packet();
		return true
	}	
}

	
/*set the next time for dropping*/
func setNextDropTime(aqm *Aqm){
	*aqm.packetsDropped+=1
	aqm.nextDropTime= time.Now().UnixNano() + int64(100/math.Sqrt(*aqm.droppedCount))
}
	

/*reset the next time for dropping, reset also the dropped packet count*/
func resetNextDropTime(aqm *Aqm){
	aqm.nextDropTime=time.Now().UnixNano() + 100 
	//todo: is it correct to set droppedCount here plus 1? maybe here =1 and in setNextDropTime +1
	*aqm.droppedCount+=1.0

}
	
/*drop packet at HEAD of queue to inform sender earlier*/
//func drop()

/*forward packet*/
//func forward_packet();