from Scheduler import Scheduler

class RoundRobin(Scheduler):
"""
RoundRobin is a a scheduler for buffering output ports. It is fairer than 
the simple FIFO strategy by not using priority. In contrast, it executes the packet cylicly cyclically

"""
    def __init__(self, queueManager):
        super(RoundRobin, self).__init__(queueManager)
        self.lastQueue = -1

    def nextQueueId(self):
        nextQueueId = self.queueManager.followingQueueId(self.lastQueue)
        start = True
        startQueueId = nextQueueId
        while startQueueId != nextQueueId or start:
            start = False
            if self.queueManager.hasQueueData(nextQueueId):
                self.lastQueue = nextQueueId
                return nextQueueId
            else:
                nextQueueId = self.queueManager.followingQueueId(nextQueueId)
        self.lastQueue = self.queueManager.previousQueueId(self.lastQueue)
        return -1
