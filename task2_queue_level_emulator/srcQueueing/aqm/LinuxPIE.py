from AQM import AQM
import random
import time
import math

class LinuxPIE(AQM):

    def __init__(self, queueName, queue_depth, target=15.0, max_bursts=150.0, max_ecnth=0.1): # In ms
        self.queueName = queueName
        self.rng = random.SystemRandom()
        self.messages = []
        self.max_bursts = max_bursts
        self.mean_pktsize = 1514
        self.max_ecnth = max_ecnth        
        # Params
        self.target = target # in ms
        self.tail_drop = float(queue_depth)
        self.alpha = 2.0 / 16
        self.beta = 20.0 / 16
        self.t_update = 15.0 * 0.001
        # Vars
        self.drop_prob = 0.0
        self.qdelay_old = 0.0
        self.current_qdelay = 0.0
        self.measurement_start = time.time() # in sec
        self.qlen_old = 0
        
        self.vars_init()

        self.calc_next = time.time() + self.t_update
    
    def vars_init(self):
        self.burst_allowance = self.max_bursts
        self.dq_count = -1
        self.accu_prob = 0.0
        self.avg_dq_time = 0.0 # in sec
        #self.accu_prob_overflows = 0.0

    def enqueue(self, queue_size, packet):
        if time.time() >= self.calc_next:
            self.calc_drop_prob(queue_size)

        if queue_size >= self.tail_drop:
            self.accu_prob = 0.0
            #self.accu_prob_overflows = 0.0
            return True
        if not self.drop_early(queue_size):
            return False
        elif False: # TODO check ecn active in packet
            pass # TODO Return ECN mark
        self.messages.append("Drop")
        self.accu_prob = 0.0
        #self.accu_prob_overflows = 0.0
        return True

    def dequeueOk(self, queue_size, packet, ecn=False):
        self.dequeue(queue_size, packet)

    def canDequeue(self, queue_size, packet):
        return True

    def dequeueDrop(self, queue_size, packet):
        pass    

    def dequeue(self, queue_size, packet):
        if time.time() >= self.calc_next:
            self.calc_drop_prob(queue_size)
        queue_threshold = 16384
        if queue_size >= queue_threshold and self.dq_count == -1.0:
            self.measurement_start = time.time()
            self.dq_count = 0   

        if self.dq_count != -1.0:
            self.dq_count = packet.getSize() + self.dq_count
            if self.dq_count >= queue_threshold:
                dq_time = (time.time() - self.measurement_start) * 1000.0
                count = self.dq_count
                if dq_time == 0.0:
                    return False
                count = count / dq_time
                if self.avg_dq_time == 0.0:
                    self.avg_dq_time = count
                else:
                    self.avg_dq_time = self.avg_dq_time * 0.75 + count * 0.25
                if queue_size < queue_threshold:
                    self.dq_count = -1.0
                else:
                    self.dq_count = 0.0
                    self.measurement_start = time.time()
                if self.burst_allowance > 0.0:
                    if self.burst_allowance > dq_time:
                        self.burst_allowance = self.burst_allowance - dq_time
                        self.messages.append("Burst" + ": {0:.15f}".format(self.burst_allowance) + ", Time: {0:.15f}".format(time.time()))
                    else:
                        self.burst_allowance = 0.0
        return False                                


    def log(self):
        with open('out/queueLinuxPIE' + self.queueName + '.log', 'w') as outfile:
            for line in self.messages:
                outfile.write(line+"\n")
            outfile.flush()


    def drop_early(self, queue_size):
        '''
            True if packet should be dropped, otherwise False.
        '''
        if self.burst_allowance > 0.0:
            return False

        if self.current_qdelay < self.target / 2.0 and self.drop_prob < 0.2:
            return False 

        if queue_size < 2 * self.mean_pktsize:
            return False  

        if self.drop_prob == 0.0:
            self.accu_prob = 0.0
            #self.accu_prob_overflows = 0.0
    

        self.accu_prob = self.accu_prob + self.drop_prob
        #self.messages.append('Accu prob'+ ", prop: {0:.15f}".format(self.accu_prob))
        #self.messages.append('Dro prob'+ ", prop: {0:.15f}".format(self.drop_prob))
        if self.accu_prob < 0.85:
            return False
        if self.accu_prob >= 8.5:
            return True
        randFloat = self.rng.random()
        #self.messages.append('Rand'+ ": {0:.15f}".format(randFloat)) 
        if randFloat < self.drop_prob:
            self.accu_prob = 0.0
            #self.accu_prob_overflows = 0.0
            return True
        else:
            return False

    def calc_drop_prob(self, queue_size):
        update_prob = True
        self.qdelay_old = self.current_qdelay
        if self.avg_dq_time > 0.0:
           self.current_qdelay = float(queue_size) / self.avg_dq_time
        else:
            self.current_qdelay = 0.0
        if self.current_qdelay == 0.0 and queue_size != 0:
            update_prob = False

        p = self.alpha * (self.current_qdelay - self.target) + self.beta * (self.current_qdelay - self.qdelay_old)

        self.messages.append("P Before" + ": {0:.15f}".format(p) + ", Time: {0:.15f}".format(time.time()))
        # TODO Check if alpha and beta are scaled in the linux like this
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

        old_prob = self.drop_prob

        if self.drop_prob >= 0.1 and p > 0.02:
            p = 0.02

        self.messages.append("P After" + ": {0:.15f}".format(p) + ", Time: {0:.15f}".format(time.time()))

        if self.current_qdelay > 250.0:
            p = p + 0.02
        
        self.drop_prob = self.drop_prob + p
        
        self.messages.append("Current Delay" + ", Delay: {0:.15f}".format(self.current_qdelay) + ", Time: {0:.15f}".format(time.time()))

        # TODO check overflow and underflow
        if p > 0.0:
            if self.drop_prob < old_prob:
                self.drop_prob = 1.0
                update_prob = False
        else:
            if self.drop_prob > old_prob:
                self.drop_prob = 0.0
                           
        if self.drop_prob < 0.0:
            self.drop_prob = 0.0
        if self.drop_prob > 1.0:
            self.drop_prob = 1.0

        if self.current_qdelay == 0.0 and self.qdelay_old == 0.0 and update_prob:
                self.drop_prob = self.drop_prob * 0.984

        
        self.messages.append("Current Prop" + ", Prop: {0:.15f}".format(self.drop_prob) + ", Time: {0:.15f}".format(time.time()))

        self.qlen_old = queue_size

        if self.current_qdelay < self.target / 2.0 and self.qdelay_old < self.target / 2.0 and self.drop_prob == 0.0 and self.avg_dq_time > 0.0:
            self.vars_init

        # Different to RFC, calc time of next calculation
        self.calc_next = time.time() + self.t_update
            




