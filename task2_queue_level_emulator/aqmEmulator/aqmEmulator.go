package main

import (
	"fmt"
	"aqmEmulator/receiver"
	"aqmEmulator/sender"
	"sync"
)


func main(){
	fmt.Println("AQM Emulator started")
	
	wg := new(sync.WaitGroup)

	iface0 := "h2-eth0"
	iface1 := "h2-eth1"

	//create queue for every interface
	
	
	//create sender for every interface (incl. ratelimiter?)
	sender0 := sender.Create(iface0)
	sender1 := sender.Create(iface1)


	//start thread0 h1 -> h3 here
	go receiver.Receive(wg, iface0, sender1)
	//start thread1 h3 -> h1 here
	go receiver.Receive(wg, iface1, sender0)


	wg.Add(2)
	wg.Wait()

}