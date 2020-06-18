from AQM import AQM
import time
import math

class CoDel(AQM):

    def __init__(self, queueName):
        self.target = 0.005 # 5ms
        self.interval = 0.1 # 100ms
        self.mtu = 1514
        self.dropping = False
        self.drop_next_packet = time.time() + self.interval
        self.count = 0
        self.messages = []
        self.last_count = 0
        self.queueName = queueName

        self.queue_size = 0

        
    def enqueue(self, queue_size, packet):
        packet.setEnqueueTimestamp(time.time())
        return False

    
    def canDequeue(self, queue_size, packet):
        now = time.time()
        packet.setDequeueTimestamp(now)
        self.queue_size = queue_size
        if packet.getQueueDelay() < self.target or queue_size < self.mtu:
            return True
        if not self.dropping and self.drop_next_packet <= now:
            return False
        if self.dropping and self.drop_next_packet <= now:
            return False
        return True    

    
    def dequeueOk(self, queue_size, packet, ecn=False):
        if ecn:
            self.dequeueDrop(queue_size, packet)
            return
        now = packet.getDequeueTimestamp()
        if packet.getQueueDelay() < self.target or self.queue_size < self.mtu:
            self.dropping = False
            self.drop_next_packet = now + self.interval


    def dequeueDrop(self, queue_size, packet):
        now = packet.getDequeueTimestamp()
        if not self.dropping and self.drop_next_packet <= now:  #go to drop state
            self.dropping = True
            self.count = self.count + 1
            #self.messages.append("Count: " + str(self.count) + ", Old_Count: " + str(self.last_count))
            delta = self.count - self.last_count
            self.count = 1
            if delta > 1 and (now - self.drop_next_packet < 16 * self.interval):
                self.messages.append("Drop Hard, Delta: " + str(delta) + ", Time: " + str(now))
                self.count = delta
            self.drop_next_packet = now + self.interval / math.sqrt(self.count)
            self.last_count = self.count
            self.messages.append("Drop Start" + ", Time: " + str(now) + ", Drop Next: {0:.15f}".format(self.drop_next_packet))
            return
        if self.dropping and self.drop_next_packet <= now:
            self.count = self.count + 1
            self.drop_next_packet = now + self.interval / math.sqrt(self.count)
            self.messages.append("Drop Normal" + ", Time: " + str(now) + ", Drop Next: {0:.15f}".format(self.drop_next_packet))            

    '''
    def dequeue(self, queue_size, packet):
        now = time.time()
        packet.setDequeueTimestamp(now)
        #self.messages.append("QueueDelay: " + str(packet.getQueueDelay()*1000) + ", Time: " + str(now))
        if packet.getQueueDelay() < self.target or queue_size < self.mtu:
            self.dropping = False
            self.drop_next_packet = now + self.interval
            return False
        if not self.dropping and self.drop_next_packet <= now:  #go to drop state
            self.dropping = True
            self.count = self.count + 1
            #self.messages.append("Count: " + str(self.count) + ", Old_Count: " + str(self.last_count))
            delta = self.count - self.last_count
            self.count = 1
            if delta > 1 and (now - self.drop_next_packet < 16 * self.interval):
                self.messages.append("Drop Hard, Delta: " + str(delta) + ", Time: " + str(now))
                self.count = delta
            self.drop_next_packet = now + self.interval / math.sqrt(self.count)
            self.last_count = self.count
            self.messages.append("Drop Start" + ", Time: " + str(now) + ", Drop Next: {0:.15f}".format(self.drop_next_packet))            
            return True
        if self.dropping and self.drop_next_packet <= now:
            self.count = self.count + 1
            self.drop_next_packet = now + self.interval / math.sqrt(self.count)
            self.messages.append("Drop Normal" + ", Time: " + str(now) + ", Drop Next: {0:.15f}".format(self.drop_next_packet))
            return True
        return False
        '''

    def log(self):
        with open('out/queueCoDel' + self.queueName + '.log', 'w') as outfile:
            for line in self.messages:
                outfile.write(line+"\n")
            outfile.flush()
