Hi guys, I'm very confused about the raw packet. So I upload code here, so you can see what I did. Fogive me, I don't know much about socket programming. Just for testing purposes. 

there are 3 main files:
1. cus_3host.py is for creating custom topology, 2 links (h1,h2) and (h2,h3)
2. icmp_raw.py is to create raw socket packet and send to h2 ( icmp packet)
3. icmp_raw_MiddleHost.py is to forward packet in both direction.

To run that:
-cd to this directory
-run command: sudo mn --custom cus_3host.py --topo mytopo
-In mininet:(Paul has shown me how to do it, and it works) 
	h2 ifconfig h2-eth1 192.168.1.2 netmask 255.255.255.0
	h3 ifconfig h3-eth0 192.168.1.3 netmask 255.255.255.0
	xterm h1
	xterm h2
	xterm h3
- At h1 window, we send a icmp raw packet to h2: python2 icmp_raw.py
- At h2 window, we execute: python2 icmp_raw_MiddleHost.py.
- At h3 window, we capture the forwarded packet: tcpdump -i h3-eth0

   
