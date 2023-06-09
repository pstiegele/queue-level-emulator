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
	var maxQueueSize int = 200
	//current queue load
	currentQueueSize0, currentQueueSize1 := 0, 0

	//scheduler tokenbucket vars
	//bucketSizeX indicates, how many tokens (=bytes) are currently in the bucket
	var bucketSize0 int64 = 0
	var bucketSize1 int64 = 0
	//tokenGenerationRate defines, how many tokens are being generated per ns
	var tokenGenerationRate float32 = 0.01 //80mbps --> 1e7 bits per 1e9 ns / 8 = 1e7/1e9 = 0,01
	//maximum size in bytes of the tokenbucket
	var maxBucketSize int64 = 1000*1500

	//vars for the active queue management
	var aqmInterval int64 = 1e8
	var aqmTarget int64 = 5e6
	var droppedCount0 float64 = 1
	var droppedCount1 float64 = 1
	packetsDropped0, packetsDropped1 := 0, 0


	//vars for console statistics
	receivedPackets0, receivedPackets1 := 0, 0
	sentPackets0, sentPackets1 := 0, 0
	
	//currentDeltaTX reflects the latest dequeue-enqueue timedelta, so for how long the packet was inside the queue
	var currentDeltaT0 float64 = 0
	var currentDeltaT1 float64 = 0
	

	//create queue for every interface
	queue0 := queue.NewQueue(maxQueueSize, &currentQueueSize0)
	queue1 := queue.NewQueue(maxQueueSize, &currentQueueSize1)

	//create active queue managements for every queue
	aqm0 := aqm.NewAqm(aqmInterval, aqmTarget, &droppedCount0, &currentDeltaT0, &packetsDropped0)
	aqm1 := aqm.NewAqm(aqmInterval, aqmTarget, &droppedCount1, &currentDeltaT1, &packetsDropped1)
	
	//create sender for every interface
	sender0 := sender.NewSender(iface0, &sentPackets0)
	sender1 := sender.NewSender(iface1, &sentPackets1)

	//create scheduler to pop packets out of the queue and give them over to the sender
	go scheduler.NewScheduler(wg, m0, queue0, sender0, aqm0, &bucketSize0, maxBucketSize, tokenGenerationRate)
	go scheduler.NewScheduler(wg, m1, queue1, sender1, aqm1, &bucketSize1, maxBucketSize, tokenGenerationRate)

	//start thread0 h1 -> h3 here
	go receiver.NewReceiver(wg, m1, iface0, queue1, createForwardingRules(0), &receivedPackets0)
	//start thread1 h3 -> h1 here
	go receiver.NewReceiver(wg, m0, iface1, queue0, createForwardingRules(1), &receivedPackets1)

	//add 4 threads to the waitgroup
	wg.Add(4)

	tm.Clear()
	i := 0
	//create the statistic screen
	for{
		tm.MoveCursor(1,1)
		//just displaying the heading with animation
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
		tm.Print(tm.Color(tm.Bold(heading+"         \n"), tm.RED)) //the spaces are to override the latest heading
		
		//packets box
		tm.MoveCursor(1,3)
		packetsBox := tm.NewBox(60, 7, 0)
		packetTable := tm.NewTable(0, 10, 5, ' ', 0)
		fmt.Fprintf(packetTable, "\tpackets received\tpackets sent\n")
		fmt.Fprintf(packetTable, "%s\t%d\t%d\n", iface0, receivedPackets0, sentPackets0)
		fmt.Fprintf(packetTable, "%s\t%d\t%d\n", iface1, receivedPackets1, sentPackets1)
		fmt.Fprintf(packetTable, "%s\t%d\t%d\n", "sum", receivedPackets0+receivedPackets1, sentPackets0 + sentPackets1)
		fmt.Fprint(packetsBox, packetTable)
		tm.Print(packetsBox.String())

		//queue box
		tm.MoveCursor(1,13)
		queueBox := tm.NewBox(60, 7, 0)
		queueTable := tm.NewTable(0, 10, 5, ' ', 0)
		fmt.Fprintf(queueTable, "\tpacket queue size [packets]\n")
		fmt.Fprintf(queueTable, "%s\t%d / %d\n", iface0, currentQueueSize0, maxQueueSize)
		fmt.Fprintf(queueTable, "%s\t%d / %d\n", iface1, currentQueueSize1, maxQueueSize)
		fmt.Fprint(queueBox, queueTable)
		tm.Print(queueBox.String())

		//schedular box
		tm.MoveCursor(1,23)
		schedulerBox := tm.NewBox(60, 7, 0)
		schedulerTable := tm.NewTable(0, 10, 5, ' ', 0)
		fmt.Fprintf(schedulerTable, "\tscheduler bucket size [bytes]\n")
		fmt.Fprintf(schedulerTable, "%s\t%d / %d\n", iface0, bucketSize0, maxBucketSize)
		fmt.Fprintf(schedulerTable, "%s\t%d / %d\n", iface1, bucketSize1, maxBucketSize)
		fmt.Fprint(schedulerBox, schedulerTable)
		tm.Print(schedulerBox.String())

		//aqm box
		tm.MoveCursor(1,33)
		aqmBox := tm.NewBox(60, 7, 0)
		aqmTable := tm.NewTable(0, 10, 5, ' ', 0)
		fmt.Fprintf(aqmTable, "aqm\tdelta T [ms]\t packets dropped\n")
		fmt.Fprintf(aqmTable, "%s\t%f\t%d\n", iface0, currentDeltaT0/1e6, packetsDropped0)
		fmt.Fprintf(aqmTable, "%s\t%f\t%d\n", iface1, currentDeltaT1/1e6, packetsDropped1)
		fmt.Fprintf(aqmTable, "%s\t%f\t%d\n", "sum", ((currentDeltaT0+currentDeltaT1)/2)/1e6, packetsDropped0+packetsDropped1)
		fmt.Fprint(aqmBox, aqmTable)
		tm.Print(aqmBox.String())

		//flush the screen and sleep for 200ms
		tm.Flush()
		time.Sleep(200 * time.Millisecond)
	}

	//in case of the for loop would end, this Waitgroup here waits for the go routines to finish (they will never be)
	wg.Wait()

}

//forwardingRules defines, which packets should be forwarded and which not. 
//because we only have 
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