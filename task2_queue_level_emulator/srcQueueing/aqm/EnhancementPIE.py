from AQM import AQM
import random
import time
import math

class EnhancementPIE(AQM):

    def __init__(self, queueName, queue_depth, target=15.0, max_bursts=150.0, max_ecnth=0.1): # In ms
        self.queueName = queueName        
        self.target = target # in ms
        self.max_bursts = max_bursts
        self.alpha = 2.0 / 16
        self.beta = 20.0 / 16
        self.t_update = 15.0 * 0.001
        self.burst_allowance = 0.0
        self.drop_prob = 0.0
        self.qdelay_old = 0.0
        self.current_qdelay = 0.0
        self.mean_pktsize = 1000
        self.calc_next = time.time() + self.t_update
        self.messages = []
        # Enhancements
        self.max_ecnth = max_ecnth
        self.dq_threshold = 2.0**14 # in bytes
        self.tail_drop = float(queue_depth)
        self.active = False
        self.accu_prob = 0.0
        self.last_timestamp = time.time() # in sec
        self.dq_count = 0
        self.measurement_start = time.time() # in sec
        self.in_measurement = True
        self.avg_dq_time = 0.0 # in sec
        self.rng = random.SystemRandom()

    def enqueue(self, queue_size, packet):
        packet.setEnqueueTimestamp(time.time())
        if time.time() >= self.calc_next:
            self.calc_drop_prob(queue_size)

        mark = False
        if queue_size + packet.getSize() > self.tail_drop:
            self.accu_prob = 0.0
            mark = True
        elif self.active and self.drop_early(queue_size) and self.burst_allowance == 0.0:        
            if self.drop_prob < self.max_ecnth and False: # TODO check ecn active in packet
                pass # TODO Return ECN mark
            else:
                self.messages.append("Drop")
                self.accu_prob = 0.0
                mark = True
        else:
            mark = False

        if not self.active and queue_size >= self.tail_drop / 3:
            self.messages.append('Active' + ", time: {0:.15f}".format(time.time()))
            self.active = True
            self.qdelay_old = 0.0
            self.drop_prob = 0.0
            self.in_measurement = True
            self.dq_count = 0
            self.avg_dq_time = 0.0
            self.last_timestamp = time.time()
            self.burst_allowance = self.max_bursts
            #self.messages.append("Burst: {0:.15f}".format(self.burst_allowance))
            self.accu_prob = 0.0
            self.measurement_start = time.time()

        
        self.current_qdelay = queue_size * self.avg_dq_time / self.dq_threshold
        self.messages.append("Measured qdelay: {0:.15f}".format(self.current_qdelay))
        if self.drop_prob == 0.0 and self.qdelay_old == 0.0 and self.current_qdelay == 0.0 and self.avg_dq_time > 0.0: # Different RFC
            self.messages.append('Passive' + ", time: {0:.15f}".format(time.time()))
            self.active = False
            self.in_measurement = False
            
        return mark

    def dequeueOk(self, queue_size, packet, ecn=False):
        self.dequeue(queue_size, packet)

    def canDequeue(self, queue_size, packet):
        return True

    def dequeueDrop(self, queue_size, packet):
        pass    

    def dequeue(self, queue_size, packet):
        qdelay_me = queue_size * self.avg_dq_time / self.dq_threshold
        packet.setDequeueTimestamp(time.time())
        qdelay_re = packet.getQueueDelay() * 1000.0
        #self.messages.append("DQ time: {0:.15f}".format(self.avg_dq_time))
        #self.messages.append("Queue Size: {0:.15f}".format(queue_size))
        #self.messages.append("Measured qdelay: {0:.15f}".format(qdelay_me))
        #self.messages.append("Real qdelay: {0:.15f}".format(qdelay_re))
        if time.time() >= self.calc_next:
            self.calc_drop_prob(queue_size)

        if self.in_measurement:
            self.dq_count = packet.getSize() + self.dq_count
            if self.dq_count >= self.dq_threshold:
                dq_time = (time.time() - self.measurement_start) * 1000.0
                if self.avg_dq_time == 0.0:
                    self.avg_dq_time = dq_time
                else:
                    weight = self.dq_threshold / 2.0**16
                    self.avg_dq_time = dq_time * weight + self.avg_dq_time * (1.0 - weight)
                self.in_measurement = False
        if queue_size >= self.dq_threshold and not self.in_measurement:
            self.in_measurement = True
            self.measurement_start = time.time()
            self.dq_count = 0

        return False

    def log(self):
        with open('out/queueEnhancementPIE' + self.queueName + '.log', 'w') as outfile:
            for line in self.messages:
                outfile.write(line+"\n")
            outfile.flush()


    def drop_early(self, queue_size):
        '''
            True if packet should be dropped, otherwise False.
        '''
        if (self.qdelay_old < self.target / 2.0 and self.drop_prob < 0.2) or (queue_size <= 2 * self.mean_pktsize):
            #self.messages.append("False 1")
            return False
        if self.drop_prob == 0.0:
            self.accu_prob = 0.0

        self.accu_prob = self.accu_prob + self.drop_prob
        #self.messages.append('Accu prob'+ ", prop: {0:.15f}".format(self.accu_prob))
        #self.messages.append('Dro prob'+ ", prop: {0:.15f}".format(self.drop_prob))
        if self.accu_prob < 0.85:
            #self.messages.append("False 2")
            return False
        if self.accu_prob >= 8.5:
            #self.messages.append("True 1")
            return True
        randFloat = self.rng.random()
        #self.messages.append('Rand'+ ": {0:.15f}".format(randFloat)) 
        if randFloat < self.drop_prob:
            self.accu_prob = 0.0
            #self.messages.append("True 2")
            return True
        else:
            #self.messages.append("False 3")
            return False

    def calc_drop_prob(self, queue_size):
        #self.messages.append('Calc prob'+ ", timediff: {0:.15f}".format(time.time() - self.last_timestamp))
        if (time.time() - self.last_timestamp) >= self.t_update and self.active:
            #self.messages.append("Queue Size: {0:.15f}".format(queue_size))
            #self.messages.append("AVG DQ: {0:.15f}".format(self.avg_dq_time))
            self.current_qdelay = queue_size * self.avg_dq_time / self.dq_threshold
            
            p = self.alpha * (self.current_qdelay - self.target) + self.beta * (self.current_qdelay - self.qdelay_old)
            self.messages.append("P Before" + ": {0:.15f}".format(p) + ", Time: {0:.15f}".format(time.time()))
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

            if self.drop_prob >= 0.1 and p > 0.02:
                p = 0.02
        
            self.messages.append("P After" + ": {0:.15f}".format(p) + ", Time: {0:.15f}".format(time.time()))
            self.drop_prob = self.drop_prob + p
            self.messages.append("Current Delay" + ", Delay: {0:.15f}".format(self.current_qdelay) + ", Time: {0:.15f}".format(time.time()))
            if self.current_qdelay < self.target / 2.0  and self.qdelay_old < self.target / 2.0:
                self.drop_prob = self.drop_prob * 0.98

            if self.drop_prob < 0.0:
                self.drop_prob = 0.0
            if self.drop_prob > 1.0:
                self.drop_prob = 1.0
        
            self.qdelay_old = self.current_qdelay

            self.messages.append("Calc Prob" + ", Prob: {0:.15f}".format(self.drop_prob) + ", Time: {0:.15f}".format(time.time()))

            self.last_timestamp = time.time()

            self.burst_allowance = max(0.0, self.burst_allowance - self.t_update * 1000.0)
            self.messages.append("Burst: {0:.15f}".format(self.burst_allowance))


        # Different to RFC, calc time of next calculation
        self.calc_next = time.time() + self.t_update
            




