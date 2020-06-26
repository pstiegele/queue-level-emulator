package aqm
//note: dropping will take place at the end of each period if the delay is over 5ms ( so last packet of each period)
//https://www-res.cablelabs.com/wp-content/uploads/2019/02/28094033/Active_Queue_Management_Algorithms_DOCSIS_3_0.pdf

interval = 100
target = 5
next_Drop_time = 0
dropped_count = 1
local_minDelay = 0  //If loca_minDelay > target, then drop() head of queue and set_nextDropTimle


/*
 set the enqueue-timestamp of packet
*/
func enqueue
	packet.setEnqueueTimestampe()

/*
Two scenarios will happend : dequeuing successfully OR drop()
1. conditon for successfully dequeing:	local_min < target OR now < next_Drop_time (even though delay > target, but when next_drop_interval has not arrived yet, we still forward packet)
2. conditon for dropping: local_min > target AND now < next_Drop_time

function will RETURN:
	TRUE if dequeue sucessfully
	FALSE if there is a drop
*/	
func dequeue 
	if (local_min > target)
		if (now < next_Drop_time)
			forward_packet();
			return true
		else
			drop()
			set_nextDropTime()  //if no packet has delay below target in 100ms, then this line is executed.
			return false
	else
		reset_nextDroptime();  //if one packet delay ever falls under target, then reset to 100ms 
		forward_packet();
		return true


	
/*set the next time for dropping*/
func set_nextDropTime() /
	next_Drop_time= time.now + 100/sqrt(dropped packet)

/*reset the next time for dropping, reset also the dropped packet count*/
func reset_nextDroptime() 
	next_Drop_time=time.now + 100 
	dropped_count=1

/*drop packet at HEAD of queue to inform sender earlier*/
func drop()

/*forward packet*/
func forward_packet();