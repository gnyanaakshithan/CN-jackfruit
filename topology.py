from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink
import time

class JobQueueTopo(Topo):
    def build(self):
        s1 = self.addSwitch('s1', protocols='OpenFlow10')
        s2 = self.addSwitch('s2', protocols='OpenFlow10')
        s3 = self.addSwitch('s3', protocols='OpenFlow10')
        s4 = self.addSwitch('s4', protocols='OpenFlow10')

        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
        h3 = self.addHost('h3', ip='10.0.0.3/24', mac='00:00:00:00:00:03')
        h4 = self.addHost('h4', ip='10.0.0.4/24', mac='00:00:00:00:00:04')
        h5 = self.addHost('h5', ip='10.0.0.5/24', mac='00:00:00:00:00:05')

        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s4)
        self.addLink(h4, s4)
        self.addLink(h5, s4)

        self.addLink(s1, s2, cls=TCLink, bw=10, delay='5ms')
        self.addLink(s2, s4, cls=TCLink, bw=10, delay='5ms')
        self.addLink(s1, s3, cls=TCLink, bw=10, delay='15ms')
        self.addLink(s3, s4, cls=TCLink, bw=10, delay='15ms')

def run():
    topo = JobQueueTopo()
    net = Mininet(topo=topo, controller=lambda name: RemoteController(name, ip='127.0.0.1', port=6633),
                  switch=OVSKernelSwitch, autoSetMacs=True)
    net.start()
    print("\n*** Waiting 6 seconds for SDN Spanning Tree to converge... ***")
    time.sleep(6)
    print("\n*** Running Pingall Check ***")
    net.pingAll()
    print("\n*** Starting Master & Workers Automatically ***")
    h3, h4, h5 = net.get('h3', 'h4', 'h5')
    h3.cmd('python3 master.py > master.log 2>&1 &')
    time.sleep(1)
    h4.cmd('python3 worker.py Worker-1 > worker1.log 2>&1 &')
    h5.cmd('python3 worker.py Worker-2 > worker2.log 2>&1 &')
    time.sleep(1)
    print("*** System Ready! Run: h1 python3 client.py C1 ***")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
