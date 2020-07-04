package main

import (
	"fmt"
	"aqmEmulator/receiver"
	"aqmEmulator/sender"
	"aqmEmulator/queue"
	"aqmEmulator/aqm"
	"aqmEmulator/scheduler"
	"sync"
	"time"
	//"log"
	tm "github.com/buger/goterm"
)

//todo: split aqm on queues

func main(){
	fmt.Println("AQM Emulator started")
	//waitgroup waits for every go routine (=thread) to finish
	wg := new(sync.WaitGroup)
	var m0 sync.Mutex
	var m1 sync.Mutex

	//interface names
	iface0 := "h2-eth0"
	iface1 := "h2-eth1"

	//maximum size of packets inside a queue
	maxQueueSize := 10000

	//scheduler tokenbucket vars
	var bucketSize0 int64 = 0
	var bucketSize1 int64 = 0
	//maximum size in bytes of scheduler tokenbucket (ratelimiter)
	var maxBucketSize int64 = 10000

	//vars for the active queue management
	var aqmInterval int64 = 100000000
	var aqmTarget int64 = 5000000
	var droppedCount0 float64 = 1
	var droppedCount1 float64 = 1
	packetsDropped0, packetsDropped1 := 0, 0


	//vars for console statistics
	receivedPackets0, receivedPackets1 := 0, 0
	sentPackets0, sentPackets1 := 0, 0
	currentQueueSize0, currentQueueSize1 := 0, 0

	var currentAverageDeltaT0 float64 = 0
	var currentAverageDeltaT1 float64 = 0
	

	//create queue for every interface
	queue0 := queue.NewQueue(maxQueueSize, &currentQueueSize0)
	queue1 := queue.NewQueue(maxQueueSize, &currentQueueSize1)

	//create active queue managements for every queue
	aqm0 := aqm.NewAqm(aqmInterval, aqmTarget, &droppedCount0, &currentAverageDeltaT0, &packetsDropped0)
	aqm1 := aqm.NewAqm(aqmInterval, aqmTarget, &droppedCount1, &currentAverageDeltaT1, &packetsDropped1)
	
	//create sender for every interface
	sender0 := sender.NewSender(iface0, &sentPackets0)
	sender1 := sender.NewSender(iface1, &sentPackets1)

	//create scheduler to pop packets out of the queue and give them over to the sender
	go scheduler.NewScheduler(wg, m0, queue0, sender0, aqm0, &bucketSize0, maxBucketSize)
	go scheduler.NewScheduler(wg, m1, queue1, sender1, aqm1, &bucketSize1, maxBucketSize)

	//start thread0 h1 -> h3 here
	go receiver.NewReceiver(wg, m1, iface0, queue1, createForwardingRules(0), &receivedPackets0)
	//start thread1 h3 -> h1 here
	go receiver.NewReceiver(wg, m0, iface1, queue0, createForwardingRules(1), &receivedPackets1)


	wg.Add(4)

	tm.Clear()
	i := 0
	//d := false
	for{
		// if(currentQueueSize0>20&&d==false){
		// 	p := queue0.Pop()
		// 	log.Println()
		// 	log.Println(p)
		// 	d=true
		// }
		tm.MoveCursor(1,1)
		
		heading := "AQM Emulator is running"
		switch i {
		case 0:
			i++
		case 1:
			heading = heading+"."
			i++
		case 2:
			heading = heading+".."
			i++
		case 3:
			heading = heading+"..."
			i++
		default:
			i = 0
			heading = heading+"...."
			
		}
		tm.Print(tm.Color(tm.Bold(heading+"         \n"), tm.RED))
		
		tm.MoveCursor(1,3)

		packetsBox := tm.NewBox(60, 7, 0)
		packetTable := tm.NewTable(0, 10, 5, ' ', 0)
		fmt.Fprintf(packetTable, "\tpackets received\tpackets sent\n")
		fmt.Fprintf(packetTable, "%s\t%d\t%d\n", iface0, receivedPackets0, sentPackets0)
		fmt.Fprintf(packetTable, "%s\t%d\t%d\n", iface1, receivedPackets1, sentPackets1)
		fmt.Fprintf(packetTable, "%s\t%d\t%d\n", "sum", receivedPackets0+receivedPackets1, sentPackets0 + sentPackets1)
		fmt.Fprint(packetsBox, packetTable)
		tm.Print(packetsBox.String())


		tm.MoveCursor(1,13)

		queueBox := tm.NewBox(60, 7, 0)
		queueTable := tm.NewTable(0, 10, 5, ' ', 0)
		fmt.Fprintf(queueTable, "\tpacket queue size\n")
		fmt.Fprintf(queueTable, "%s\t%d / %d\n", iface0, currentQueueSize0, maxQueueSize)
		fmt.Fprintf(queueTable, "%s\t%d / %d\n", iface1, currentQueueSize1, maxQueueSize)
		fmt.Fprint(queueBox, queueTable)
		tm.Print(queueBox.String())

		tm.MoveCursor(1,23)

		schedulerBox := tm.NewBox(60, 7, 0)
		schedulerTable := tm.NewTable(0, 10, 5, ' ', 0)
		fmt.Fprintf(schedulerTable, "\tscheduler bucket size\n")
		fmt.Fprintf(schedulerTable, "%s\t%d / %d\n", iface0, bucketSize0, maxBucketSize)
		fmt.Fprintf(schedulerTable, "%s\t%d / %d\n", iface1, bucketSize1, maxBucketSize)
		fmt.Fprint(schedulerBox, schedulerTable)
		tm.Print(schedulerBox.String())

		tm.MoveCursor(1,33)

		aqmBox := tm.NewBox(60, 7, 0)
		aqmTable := tm.NewTable(0, 10, 5, ' ', 0)
		fmt.Fprintf(aqmTable, "aqm\tdeltaT in ms\t packets dropped\n")
		fmt.Fprintf(aqmTable, "%s\t%f\t%d\n", iface0, currentAverageDeltaT0*0.000001, packetsDropped0)
		fmt.Fprintf(aqmTable, "%s\t%f\t%d\n", iface0, currentAverageDeltaT1*0.000001, packetsDropped1)
		fmt.Fprintf(aqmTable, "%s\t%f\t%d\n", "sum", (currentAverageDeltaT0*0.000001+currentAverageDeltaT1*0.000001)/2, packetsDropped0+packetsDropped1)
		fmt.Fprint(aqmBox, aqmTable)
		tm.Print(aqmBox.String())

		tm.Flush()
		time.Sleep(1 * time.Second)
	}


	wg.Wait()

}


func createForwardingRules(direction int) receiver.ForwardingRules{
	if(direction == 0){
		fr := receiver.ForwardingRules{
			Src: []byte{0, 0, 0, 0, 0, 1},
			Dest: []byte{0, 0, 0, 0, 0, 3}}
		return fr
	}else{
		fr := receiver.ForwardingRules{
			Src: []byte{0, 0, 0, 0, 0, 3},
			Dest: []byte{0, 0, 0, 0, 0, 1}}
		return fr
	}
}