package main

import (
	"fmt"
	"aqmEmulator/receiver"
	"aqmEmulator/sender"
	"aqmEmulator/queue"
	"aqmEmulator/scheduler"
	"sync"
)


func main(){
	fmt.Println("AQM Emulator started")
	
	wg := new(sync.WaitGroup)

	iface0 := "h2-eth0"
	iface1 := "h2-eth1"

	//create queue for every interface
	queue0 := queue.NewQueue(10)
	queue1 := queue.NewQueue(10)
	
	//create sender for every interface (incl. ratelimiter?)
	sender0 := sender.NewSender(iface0)
	sender1 := sender.NewSender(iface1)

	//create scheduler to pop packets out of the queue and give them over to the sender
	go scheduler.NewScheduler(wg, queue0, sender0)
	go scheduler.NewScheduler(wg, queue1, sender1)

	//todo: what should take out the packets and give them to the sender? the aqm? the rate limiter? the aqm and then the rate limiter? or the other way around?
	_, _ = sender0, sender1

	
	//start thread0 h1 -> h3 here
	go receiver.NewReceiver(wg, iface0, queue1, createForwardingRules(0))
	//start thread1 h3 -> h1 here
	go receiver.NewReceiver(wg, iface1, queue0, createForwardingRules(1))


	wg.Add(2)
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