from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo

class ThreeHostsTopology(Topo):
    def __init__(self):
        Topo.__init__(self)
        host1_id = self.addHost('h1', ip='10.0.0.1/24')
        host2_id = self.addHost('h2')
        host3_id = self.addHost('h3', ip='10.0.0.3/24')
        self.addLink(host1_id, host2_id)
        self.addLink(host3_id, host2_id)

def configure_network(network):
    h1 = network.get('h1')
    h2 = network.get('h2')
    h3 = network.get('h3')

if __name__ == '__main__':
    setLogLevel('info')
    net = Mininet(topo=ThreeHostsTopology(), autoSetMacs= True)
    configure_network(net)
    CLI(net)
