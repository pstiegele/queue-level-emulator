from Scheduler import Scheduler
from collections import deque

class FQScheduler(Scheduler):
    """Fair Queueing scheduler is used for buffering output(not input like AQM)
    quantum: maximum time slot that a process can be process  
    """
    def __init__(self, queueManager, quantum):
        super(FQScheduler, self).__init__(queueManager)
        self.quantum = quantum
        self.newQueue = deque()
        self.oldQueue = deque()
        self.queuesQuantum = dict()

    def nextQueueId(self):
        # TODO If rate limiter doesn't allow sending we reduced the quantum of the queue!
        while True:
            #print("Length dict: " + str(len(self.queuesQuantum)) + " Length new Queues: " + str(len(self.newQueue)) + " Length old Queue: "  + str(len(self.oldQueue)))
            try:
                queueId = self.newQueue.popleft()
            except IndexError: # empty
                queueId = -1   
            if queueId != -1: # newQueue
                if self.queuesQuantum[queueId] > 0 and self.queueManager.hasQueueData(queueId): # Queue can be dequeued
                    # TODO negative quantum ? -> RFC yes
                    packetSize = self.queueManager.sizeOfFirstPacket(queueId)
                    self.queuesQuantum[queueId] = self.queuesQuantum[queueId] - packetSize
                    self.newQueue.appendleft(queueId)
                    return queueId
                else: # to oldQueue with new quantum
                    self.queuesQuantum[queueId] = self.queuesQuantum[queueId] + self.quantum
                    self.oldQueue.append(queueId)        
            else: # oldQueue            
                try:
                    queueId = self.oldQueue.popleft()
                except IndexError: # empty
                    queueId = -1
                if queueId != -1:
                    if self.queueManager.hasQueueData(queueId): #
                        if self.queuesQuantum[queueId] > 0:
                            # TODO negative quantum ? -> RFC yes
                            packetSize = self.queueManager.sizeOfFirstPacket(queueId)
                            self.queuesQuantum[queueId] = self.queuesQuantum[queueId] - packetSize
                            self.oldQueue.appendleft(queueId)
                            return queueId    
                        else: # add at the end with new quantum
                            self.queuesQuantum[queueId] = self.queuesQuantum[queueId] + self.quantum
                            self.oldQueue.append(queueId) 
                    else: # remove queue from oldQueue -> already done, delete from dict
                        del self.queuesQuantum[queueId]            
                else: # all queues are empty
                    return -1            

    def queueClassified(self, queueId):
        if queueId not in self.queuesQuantum:
            self.queuesQuantum[queueId] = self.quantum
            self.newQueue.append(queueId)

