from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
import subprocess


h1_ip = "10.0.0.1"
h2_ip_eth0 = "10.0.0.2"
h2_ip_eth1 = "10.0.0.2"
h3_ip = "10.0.0.3"

class ThreeHostsTopology(Topo):
    def __init__(self):
        Topo.__init__(self)
        host1_id = self.addHost('h1', ip=h1_ip+'/24')
        host2_id = self.addHost('h2')
        host3_id = self.addHost('h3', ip=h3_ip+'/24')
        self.addLink(host1_id, host2_id)
        self.addLink(host3_id, host2_id)

def whichLanguage():
    print()
    print()
    print("***** Which language do you want to use for packet forwarding?")
    print()
    print("0: No implementation, just net.ipv4.ip_forward=1")
    print("1: Python")
    print("2: C")
    print("3: Go")
    print()
    return input()


def whatToEvaluate():
    print()
    print()
    print("***** What do you want to evaluate?")
    print()
    print("0: Nothing")
    print("1: Ping")
    print("2: Iperf3 TCP")
    print("3: Iperf3 UDP")
    print()
    return input()


def startPacketForwarding(network, language):    
    h1 = network.get('h1')
    h2 = network.get('h2')
    h3 = network.get('h3')
    h1.cmd('ethtool --offload h1-eth0 rx off tx off ') # disable tcp checksums
    h3.cmd('ethtool --offload h3-eth0 rx off tx off ') # disable tcp checksums

    if language == "0": # ip_forward=1
        h2.setIP(h2_ip_eth0+'/24', intf='h2-eth0')
        h2.setIP(h2_ip_eth1+'/24', intf='h2-eth1')
        h2.cmd('sudo sysctl net.ipv4.ip_forward=1')
        h1.cmd('ip route add default via '+h2_ip_eth0+' dev h1-eth0')
        h3.cmd('ip route add default via '+h2_ip_eth1+' dev h3-eth0')
    
    if language == "1": # Python
        print("not yet implemented")

    if language == "2": # C
        print("not yet implemented")

    if language == "3": # Go
        h2.cmd('/usr/local/go/bin/go build -o golang/ golang/src/forwardTraffic/forwardTraffic.go')
        h2.cmd('./golang/forwardTraffic &')


def startEvaluation(network, evaluation):
    h1 = network.get('h1')
    # h2 = network.get('h2')
    h3 = network.get('h3')
    print()
    print()
    print()

    if evaluation == "0":
        print("***** no evaluation selected")

    if evaluation == "1":
        print("***** Evaluate Ping:")
        print()
        print("h1 --> h3:")
        res = h1.cmd('ping '+h3_ip+' -c 2')
        print(res)
        print()
        print("h3 --> h1:")
        res = h3.cmd('ping '+h1_ip+' -c 2')
        print(res)

    if evaluation == "2":
        print("***** Evaluate TCP Bandwith with iperf3:")
        print()
        res1 = h1.cmd("iperf3 -s &")
        res3 = h3.cmd("iperf3 -c "+h1_ip)
        print("h1 output:")
        print(res1)
        print("h3 output:")
        print(res3)

    if evaluation == "3":
        print("***** Evaluate UDP Bandwith with iperf3:")
        print()
        res1 = h1.cmd("iperf3 -s &")
        res3 = h3.cmd("iperf3 -u -c "+h1_ip)
        print("h1 output:")
        print(res1)
        print("h3 output:")
        print(res3)
    
    print()
    print()
    print()



if __name__ == '__main__':
    setLogLevel('info')
    language = whichLanguage()
    if language == "0": # if language=0 change ips so that h1 and h3 are in different networks
        h1_ip = "10.0.1.1"
        h2_ip_eth0 = "10.0.1.2"
        h2_ip_eth1 = "10.0.3.2"
        h3_ip = "10.0.3.1"
    evaluation = whatToEvaluate()
    net = Mininet(topo=ThreeHostsTopology(), autoSetMacs= True)
    startPacketForwarding(net, language)
    startEvaluation(net, evaluation)
    CLI(net)
