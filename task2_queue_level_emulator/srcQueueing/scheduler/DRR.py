from Scheduler import Scheduler

class DRR(Scheduler):

    def __init__(self, queueManager, quantum):
        super(DRR, self).__init__(queueManager)
        self.lastQueue = -1
        self.quantum = quantum
        self.qQuan = list()
        for i in range(0, self.queueManager.numQueues()):
            self.qQuan.append(0)

    def nextQueueId(self):
        if self.lastQueue == -1:
            nextQueueId = self.queueManager.followingQueueId(self.lastQueue)
            next = True
        else:
            nextQueueId = self.lastQueue
            next = False
        start = True
        startQueueId = nextQueueId
        while startQueueId != nextQueueId or start:
            start = False
            if self.queueManager.hasQueueData(nextQueueId):
                if next:
                    self.qQuan[nextQueueId] = self.qQuan[nextQueueId] + self.quantum
                packetSize = self.queueManager.sizeOfFirstPacket(nextQueueId)     
                if self.qQuan[nextQueueId] > packetSize:
                    self.qQuan[nextQueueId] = self.qQuan[nextQueueId] - packetSize                     
                    self.lastQueue = nextQueueId
                    return nextQueueId
                else:
                    nextQueueId = self.queueManager.followingQueueId(nextQueueId)
                    next = True
            else:
                self.qQuan[nextQueueId] = 0
                nextQueueId = self.queueManager.followingQueueId(nextQueueId)
                next = True
        self.lastQueue = self.queueManager.previousQueueId(self.lastQueue)
        return -1
