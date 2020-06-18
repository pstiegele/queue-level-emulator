from mininet.node import Node
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.link import Link

import os
import time

from srcQueueing.QueueingHost import QueueingHost

useLinuxRouter = False

class NetworkTopo(Topo):
    def build(self, **opts):
        # Hosts
        client = self.addHost('client', ip='10.0.0.2/24')#, defaultRoute='via 10.0.1.254 dev eth0')
        server1 = self.addHost('server1', ip='10.0.2.2/24')#, defaultRoute='via 10.0.1.254 dev eth0')
        server2 = self.addHost('server2', ip='10.0.3.2/24')#, defaultRoute='via 10.0.1.254 dev eth0')
        if useLinuxRouter:
            bng = self.addHost('bng', ifNames={'ifName1': 'bng-eth0', 'ifName2': 'bng-eth1'})
        else:
            bng = self.addHost('bng', cls=QueueingHost, ifNames={'ifName1': 'bng-eth0', 'ifName2': 'bng-eth1'})
        intermed = self.addHost('intermed')
        # Links
        self.addLink(client, bng)#, delay="1ms", bw=500)
        self.addLink(server1, intermed, cls=TCLink, delay="5ms")#, delay="1ms", bw=200)
        self.addLink(server2, intermed, cls=TCLink, delay="5ms")#, delay="1ms", bw=200)
        self.addLink(bng, intermed)#, delay="1ms", bw=500)


def main():
    topo = NetworkTopo()
    mn = Mininet(topo=topo, link=Link)
    for h in mn.hosts:
        h.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        h.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        h.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
    bng = mn.getNodeByName('bng')
    intermed = mn.getNodeByName('intermed')
    server1 = mn.getNodeByName('server1')
    server2 = mn.getNodeByName('server2')
    client = mn.getNodeByName('client')
    bng.cmd('ifconfig bng-eth0 10.0.0.1 netmask 255.255.255.0')
    bng.cmd('ifconfig bng-eth1 10.0.1.1 netmask 255.255.255.0')
    if useLinuxRouter:    
        bng.cmd('sysctl -w net.ipv4.ip_forward=1')
        bng.cmd('tc qdisc add dev bng-eth1 handle 1: root htb default 11')
        bng.cmd('tc class add dev bng-eth1 parent 1: classid 1:11 htb rate 10000kbit')
        #bng.cmd('tc qdisc add dev bng-eth1 parent 1:11 handle 2:0 codel limit 413 ecn')
        bng.cmd('tc qdisc add dev bng-eth1 parent 1:11 handle 2:0 pie limit 413 target 15ms tupdate 15ms')
    print(bng.cmd('tc qdisc'))
    intermed.cmd('ifconfig intermed-eth0 10.0.2.1 netmask 255.255.255.0')
    intermed.cmd('ifconfig intermed-eth1 10.0.3.1 netmask 255.255.255.0')
    intermed.cmd('ifconfig intermed-eth2 10.0.1.2 netmask 255.255.255.0') 
    intermed.cmd('sysctl -w net.ipv4.ip_forward=1')
    print(intermed.cmd('tc qdisc'))   
    server1.cmd('ip route add 10.0.0.0/24 dev server1-eth0 via 10.0.2.1')
    server2.cmd('ip route add 10.0.0.0/24 dev server2-eth0 via 10.0.3.1')
    client.cmd('ip route add 10.0.2.0/24 dev client-eth0 via 10.0.0.1')
    client.cmd('ip route add 10.0.3.0/24 dev client-eth0 via 10.0.0.1')
    intermed.cmd('ip route add 10.0.0.0/24 dev intermed-eth2 via 10.0.1.1')
    bng.cmd('ip route add 10.0.2.0/24 dev bng-eth1 via 10.0.1.2')
    bng.cmd('ip route add 10.0.3.0/24 dev bng-eth1 via 10.0.1.2')

    #Deactivate offloading
    client.cmd('ethtool --offload client-eth0 rx off tx off')
    server1.cmd('ethtool --offload server1-eth0 rx off tx off')
    server2.cmd('ethtool --offload server2-eth0 rx off tx off')

    #Activate ECN
    client.cmd('sysctl -w net.ipv4.tcp_ecn=1')
    server1.cmd('sysctl -w net.ipv4.tcp_ecn=1')
    server2.cmd('sysctl -w net.ipv4.tcp_ecn=1')

    #Change Congestion Control
    #client.cmd('sysctl -w net.ipv4.tcp_congestion_control=reno')
    print(client.cmd('sysctl net.ipv4.tcp_congestion_control'))

    mn.start()
    if not useLinuxRouter:
        bng.start()
    bng.cmd('tcpdump tcp and src 10.0.0.2 -i bng-eth0 -w out/in.pcap &')
    bng.cmd('tcpdump tcp and src 10.0.0.2 -i bng-eth1 -w out/out.pcap &')
    #CLI(mn)
    time.sleep(1)
    server1.cmd('iperf3 -s -D')
    server2.cmd('iperf3 -s -D')
    #server2.cmd('iperf -s -D')
    #client.cmd('iperf3 -c 10.0.2.2 -t 10 -J -P 1 -i 0.25 -M 1000 > out/iperf_client_1.json &')
    #time.sleep(15)
    client.cmd('iperf3 -c 10.0.3.2 -t 10 -J -P 1 -i 0.25 > out/iperf_client_2.json')  
    #client.cmd('iperf -c 10.0.3.2 -u --bandwidth 11M -t 15 -i 0.25 > out/iperf_client_2.json')      #use only iperf2 for udp tests, iperf3 creates bigger micro bursts
    #CLI(mn)
    open('stopQueueingRunner', 'a').close()
    time.sleep(3)
    mn.stop()
    os.system('pkill iperf3')



if __name__ == '__main__':
    setLogLevel( 'info' )
    main()




