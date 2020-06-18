import time
import random
from AQM import AQM

class RED(AQM):

    def __init__(self, queueName, queue_depth_bytes, rateLimiterBW, queue_weight = 0.02, max_p = 0.02):
        self.queue_weight = queue_weight
        self.max_queue_thres = float(queue_depth_bytes) / 4
        self.min_queue_thres = float(self.max_queue_thres) / 3
        #self.max_queue_thres = 0.99 * queue_depth_bytes
        #self.min_queue_thres = 0.8 * queue_depth_bytes
        self.max_p = max_p
        self.avg = 0.0
        self.count = -1
        self.q_time = time.time()
        self.bandwidth = float(rateLimiterBW)
        self.avg_pkt_size = 1000.0
        self.messages = []
        self.queueName = queueName
        self.rng = random.SystemRandom()

    def enqueue(self, queue_size, packet):
        mark = False
        #Calc avg
        if queue_size != 0:
            self.avg = (1-self.queue_weight) * self.avg + self.queue_weight * queue_size
        else:
            m = (time.time()-self.q_time) / (self.avg_pkt_size / self.bandwidth)
            self.avg = ((1-self.queue_weight)**m) * self.avg
        self.messages.append("Avg: " + str(self.avg))

        if self.avg >= self.min_queue_thres and self.avg <= self.max_queue_thres:
            self.count = self.count + 1
            pb = (self.avg-self.min_queue_thres)/(self.max_queue_thres-self.min_queue_thres)*self.max_p
            pa = pb / (1 - self.count * pb)
            self.messages.append("Between: " + str(pa))
            if pa > self.rng.random():
                self.messages.append("Drop")
                mark = True
                self.count = 0
        elif self.avg > self.max_queue_thres:
            self.messages.append("Greater Drop")
            mark = True
            self.count = 0
        else:
            self.messages.append("Smaller")
            self.count = -1
 
        return mark

    def dequeueOk(self, queue_size, packet, ecn=False):
        if (queue_size - packet.getSize()) <= 0:
            self.q_time = time.time()

    def canDequeue(self, queue_size, packet):
        return True

    def dequeueDrop(self, queue_size, packet):
        pass
        
    def log(self):
        with open('out/queueRed' + self.queueName + '.log', 'w') as outfile:
            for line in self.messages:
                outfile.write(line+"\n")
