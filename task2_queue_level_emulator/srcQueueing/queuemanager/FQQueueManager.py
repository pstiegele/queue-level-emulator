from QueueManager import QueueManager
from queue.VirtualQueue import VirtualQueue
from queue.PacketQueue import PacketQueue
from ratelimiter.Tokenbucket import Tokenbucket
from aqm.RED import RED
from aqm.CoDel import CoDel
from aqm.BasicPIE import BasicPIE
from aqm.EnhancementPIE import EnhancementPIE
from aqm.LinuxPIE import LinuxPIE

rate = 10*1000*1000/8 #1 = 1 byte per second
queue_depth = rate * 0.5#0.05
MTU = 1514
burstRate = 5000


class FQQueueManager(QueueManager):

    def __init__(self, numberQueues=32):
        # FQ uses a list for new queues and old queues
        self.queues = dict() # Red black tree is the best data structure for Stochastic Fair Queueing 
        self.numberQueues = numberQueues

        self.vQueue = VirtualQueue('vQueue', rateLimiter=Tokenbucket(rate, MTU, burstRate), depthBytes=queue_depth*self.numberQueues)

        for x in range (0, numberQueues):
            self.queues[x] = PacketQueue(str(x), rateLimiter=None, depthBytes=queue_depth, aqm=CoDel(queueName=str(x)), parentQueue=self.vQueue)

    def numQueues(self):
        return self.numberQueues

    def followingQueueId(self, currentQueueId):
        if currentQueueId + 1 >= self.numberQueues:
            return 0
        else:
            return currentQueueId + 1

    def previousQueueId(self, currentQueueId):
        if currentQueueId - 1 < 0:
            return self.numberQueues - 1
        else:
            return currentQueueId - 1        

    def getLongestQueue(self, queueId):
        size = 0
        index = 0
        for q in range(0, self.numberQueues):
            currentByteLength = self.queues[q].getByteLength()
            if currentByteLength > size or (currentByteLength == size and q == currentQueue):
                size = self.queues[q].getByteLength()
                index = q
        return index

    def hasQueueData(self, queueId):
        return self.queues[queueId].getPaketLength() > 0

    def queueSize(self, queueId):
        return self.queues[queueId].getPacketLength()    

    def canPop(self, queueId):
        return self.queues[queueId].canPop()

    def pop(self, queueId, drop=False):
        return self.queues[queueId].pop(drop=drop)

    def aqmDequeueOk(self, queueId, packet, ecn=False):
        self.queues[queueId].aqmDequeueOk(packet, ecn=ecn)

    def aqmDequeueDrop(self, queueId, packet):
        self.queues[queueId].aqmDequeueDrop(packet)

    def rateLimiterSend(self, queueId, packet):
        self.queues[queueId].rateLimiterSend(packet)

    def canPush(self, queueId, packet):
        return self.queues[queueId].canPush(packet)

    def push(self, queueId, packet):
        self.queues[queueId].push(packet)

    def tailpop(self, queueId, drop=False):
        return self.queues[queueId].tailpop(packet, drop=drop)

    def markEcnFirstPacket(self, queueId):
        self.queues[queueId].markEcnFirstPacket()

    def sizeOfFirstPacket(self, queueId):
        return self.queues[queueId].sizeOfFirstPacket()

    def log(self):
        self.vQueue.log()
        for x in range(0, self.numberQueues):
            self.queues[x].log()    
