package main

import (
	"fmt"
	"aqmEmulator/receiver"
	"aqmEmulator/sender"
	"aqmEmulator/queue"
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

	//todo: what should take out the packets and give them to the sender? the aqm? the rate limiter? the aqm and then the rate limiter? or the other way around?
	_, _ = sender0, sender1

	//start thread0 h1 -> h3 here
	go receiver.NewReceiver(wg, iface0, queue1)
	//start thread1 h3 -> h1 here
	go receiver.NewReceiver(wg, iface1, queue0)


	wg.Add(2)
	wg.Wait()

}