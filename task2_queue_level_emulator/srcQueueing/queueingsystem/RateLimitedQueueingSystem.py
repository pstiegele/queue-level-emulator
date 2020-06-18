from QueueingSystem import QueueingSystem
from queue.PacketQueue import *
from Packet import *
from ratelimiter.Tokenbucket import Tokenbucket
from utils.utils import *
import time, sys

rate = 10*1000*1000/8 #1 = 1 byte per second
queue_depth = rate * 0.05
MTU = 1514
burstRate = 5000

#TODO change to match new Queue design
class RateLimitedQueueingSystem(QueueingSystem):
    def __init__(self, numberQueues):
        self.queues = dict()
        self.numberQueues = numberQueues
        self.sentPackets = dict()

        self.last_scheduled_queue = 0

        for x in range (0, numberQueues):
            self.queues[x] = Queue(str(x), rateLimiter=Tokenbucket(rate, MTU, burstRate), depthBytes=queue_depth)
            self.sentPackets[x] = []

    def getQueueId(self, packet):
        if packet.getIPv4DstAddress() == ip2int('10.0.3.2'):
            return 1
        return 0
        #return packet.getIPv4DstAddress() % self.numberQueues

    def insertPacket(self, packet):
        queueId = self.getQueueId(packet)
        self.queues[queueId].push(packet)


    def callDequeueScheduler(self):
        #self.updateRateLimiter()
        for q in range(self.last_scheduled_queue, self.numberQueues) + range(0, self.last_scheduled_queue):
            rateLimiter = self.queues[q].getRateLimiter()             
            rateLimiter.update()            
            if(rateLimiter.canSendPacket()):
                packet = self.queues[q].pop()
                if packet != None:
                    rateLimiter.packetSent(packet.getSize()) #update tokens of this queue
                    self.last_scheduled_queue = q
                    #self.sentPackets[q].append(packet)
                    return packet
        return None

    
    def getSentPackets(self, queueId):
        return self.sentPackets[queueId]

    def log(self):
        for x in range(0, self.numberQueues):
            self.queues[x].log()
