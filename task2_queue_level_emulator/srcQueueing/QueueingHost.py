from mininet.node import Node

class QueueingHost(Node):
    def __init__(self, name, inNamespace=True, **params):
        super(QueueingHost, self).__init__(name, inNamespace, **params);
        
        self.ifName1 = params['ifNames']['ifName1']
        self.ifName2 = params['ifNames']['ifName2']


    def start(self):
        self.cmd('srcQueueing/queueingRunner.py 2>&1 | tee out/'+self.name+'_stdout.txt &')
        print("Start Queueing Runner ")

    def terminate(self):
        self.cmd('pkill queueingRunner.')     

    
