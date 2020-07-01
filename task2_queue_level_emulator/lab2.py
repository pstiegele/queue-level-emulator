from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
import subprocess
import os


h1_ip = "10.0.0.1"
h2_ip_eth0 = "10.0.0.2"
h2_ip_eth1 = "10.0.0.2"
h3_ip = "10.0.0.3"
process_name = ""

class ThreeHostsTopology(Topo):
    def __init__(self):
        Topo.__init__(self)
        host1_id = self.addHost('h1', ip=h1_ip+'/24')
        host2_id = self.addHost('h2')
        host3_id = self.addHost('h3', ip=h3_ip+'/24')
        self.addLink(host1_id, host2_id)
        self.addLink(host3_id, host2_id)

def startAQMEmulator(network):    
    h1 = network.get('h1')
    h2 = network.get('h2')
    h3 = network.get('h3')
    h1.cmd('ethtool --offload h1-eth0 rx off tx off ') # disable tcp checksums
    h3.cmd('ethtool --offload h3-eth0 rx off tx off ') # disable tcp checksums

    print("***** build aqm emulator")
    h2.cmd('cd aqmEmulator')
    h2.cmd('/usr/local/go/bin/go build -o ./ aqmEmulator.go')
    #print("***** run aqm emulator")
    h2.cmd('chmod +x ./aqmEmulator')
    #h2.cmd('./aqmEmulator &')



if __name__ == '__main__':
    os.system('sudo mn -c')
    setLogLevel('info')
    net = Mininet(topo=ThreeHostsTopology(), autoSetMacs= True)
    startAQMEmulator(net)
    CLI(net)