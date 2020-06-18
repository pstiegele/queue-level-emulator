from AQM import AQM
import random
import time

class BasicPIE(AQM):

    def __init__(self, queueName, target=15.0, max_bursts=150.0): # In ms
        self.queueName = queueName        
        self.target = target # in ms
        self.max_bursts = max_bursts * 0.001
        self.alpha = 1.0/8
        self.beta = 1.0 + 1.0/4
        self.t_update = 15.0 * 0.001
        self.burst_allowance = 0.0
        self.drop_prob = 0.0
        self.qdelay_old = 0.0
        self.current_qdelay = 0.0
        self.mean_pktsize = 1000
        self.calc_next = time.time() + self.t_update
        self.messages = []
        self.rng = random.SystemRandom()

    def enqueue(self, queue_size, packet):
        packet.setEnqueueTimestamp(time.time())
        if time.time() >= self.calc_next:
            self.calc_drop_prob()
        if self.drop_prob == 0.0 and self.current_qdelay < self.target / 2 and self.qdelay_old < self.target / 2:
            self.burst_allowance = self.max_bursts
        if self.burst_allowance == 0 and self.drop_early(queue_size):
            self.messages.append("Drop " + ", Time: {0:.15f}".format(time.time()))            
            return True
        else:
            return False       
             
    def dequeueOk(self, queue_size, packet, ecn=False):
        self.dequeue(queue_size, packet)

    def canDequeue(self, queue_size, packet):
        return True

    def dequeueDrop(self, queue_size, packet):
        pass    

    def dequeue(self, queue_size, packet):
        if time.time() >= self.calc_next:
            self.calc_drop_prob()
        packet.setDequeueTimestamp(time.time())
        self.current_qdelay = packet.getQueueDelay() * 1000.0
        return False

    def log(self):
        with open('out/queueBasicPIE' + self.queueName + '.log', 'w') as outfile:
            for line in self.messages:
                outfile.write(line+"\n")
            outfile.flush()


    def drop_early(self, queue_size):
        '''
            True if packet should be dropped, otherwise False.
        '''
        if (self.qdelay_old < self.target / 2 and self.drop_prob < 0.2) or (queue_size <= 2 * self.mean_pktsize):
            #self.messages.append("Drop Early 1" + ", Time: {0:.15f}".format(time.time()))            
            return False
        randFloat = self.rng.random()
        #self.messages.append("Drop Prob" + ", Prob: {0:.15f}".format(self.drop_prob) + ", Time: {0:.15f}".format(time.time()))
        #self.messages.append("Drop Rand" + ", Prob: {0:.15f}".format(randFloat) + ", Time: {0:.15f}".format(time.time()))                        
        if randFloat < self.drop_prob:
            #self.messages.append("Drop Early 2" + ", Time: {0:.15f}".format(time.time()))            
            return True
        else:
            #self.messages.append("Drop Early 3" + ", Time: {0:.15f}".format(time.time()))            
            return False

    def calc_drop_prob(self):
        #self.messages.append("Calc Prob " + ", Time: {0:.15f}".format(time.time()))
        p = self.alpha * (self.current_qdelay - self.target) + self.beta * (self.current_qdelay - self.qdelay_old)
        if self.drop_prob < 0.000001:
            p = p / 2048
        elif self.drop_prob < 0.00001:
            p = p / 512
        elif self.drop_prob < 0.0001:
            p = p / 128
        elif self.drop_prob < 0.001:
            p = p / 32
        elif self.drop_prob < 0.01:
            p = p / 8
        elif self.drop_prob < 0.1:
            p = p / 2
        
        self.drop_prob = self.drop_prob + p
        self.messages.append("Current Delay" + ", Delay: {0:.15f}".format(self.current_qdelay) + ", Time: {0:.15f}".format(time.time()))
        if self.current_qdelay == 0.0 and self.qdelay_old == 0.0:
            self.drop_prob = self.drop_prob * 0.98

        if self.drop_prob < 0.0:
            self.drop_prob = 0.0
        if self.drop_prob > 1.0:
            self.drop_prob = 1.0
        
        self.qdelay_old = self.current_qdelay

        self.messages.append("Calc Prob" + ", Prob: {0:.15f}".format(self.drop_prob) + ", Time: {0:.15f}".format(time.time()))

        self.burst_allowance = max(0.0, self.burst_allowance - self.t_update)

        # Different to RFC, calc time of next calculation
        self.calc_next = time.time() + self.t_update
            




