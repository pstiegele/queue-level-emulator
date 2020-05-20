from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo

class ThreeHostsTopology(Topo):
    def __init__(self):
        Topo.__init__(self)
        host1_id = self.addHost('h1', ip='10.0.1.1/24')
        host2_id = self.addHost('h2')
        host3_id = self.addHost('h3', ip='10.0.3.1/24')
        self.addLink(host1_id, host2_id)
        self.addLink(host3_id, host2_id)

def configure_network(network):
    h1 = network.get('h1')
    h2 = network.get('h2')
    h3 = network.get('h3')
    
    h2.setIP('10.0.1.2/24', intf='h2-eth0')
    h2.setIP('10.0.3.2/24', intf='h2-eth1')
    h2.cmd('sudo sysctl net.ipv4.ip_forward=1')
    
    h1.cmd('ip route add default via 10.0.1.2 dev h1-eth0')
    h3.cmd('ip route add default via 10.0.3.2 dev h3-eth0')


if __name__ == '__main__':
    setLogLevel('info')
    net = Mininet(topo=ThreeHostsTopology())
    configure_network(net)
    net.pingAll()
    CLI(net)
