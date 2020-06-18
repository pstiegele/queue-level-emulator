from utils.utils import *
import time

class DequeueManager(object):

    def __init__(self, queueManager, scheduler, ECN=False):
        self.queueManager = queueManager
        self.scheduler = scheduler
        self.ECN = ECN
        self.dropList = []

    def getLog(self):
        return self.dropList    

    def getPacket(self):
        '''
            Get the next packet for transmitting. 
            Returns None if no packet is available.
        '''
        while True:
            nextQueueId = self.scheduler.nextQueueId()
            if nextQueueId == -1:
                return None
            else:        
                resCode = self.queueManager.canPop(nextQueueId)
                if resCode == 0:            
                    packet = self.queueManager.pop(nextQueueId)
                    self.queueManager.aqmDequeueOk(nextQueueId, packet)
                    return packet
                if getBitAtPosition(resCode, 2) == 1: # RateLimiter not OK
                    continue    
                if getBitAtPosition(resCode, 3) == 1: # AQM not OK   
                    if not self.ECN:
                        packet = self.queueManager.pop(nextQueueId, drop=True)
                        self.dropList.append({'time': time.time(), 'dropQueue': nextQueueId, 'dropState': 'AQM Dequeue'})
                        self.queueManager.aqmDequeueDrop(nextQueueId, packet)
                        continue
                    elif getBitAtPosition(resCode, 2) == 0:
                        packet = self.queueManager.pop(nextQueueId, drop=True) # True doesn't change rate limiter must be set manually
                        if packet.hasECN():
                            self.queueManager.rateLimiterSend(nextQueueId, packet)
                            self.dropList.append({'time': time.time(), 'dropQueue': nextQueueId, 'dropState': 'AQM Dequeue ECN'})
                            packet.ecnMark()
                            self.queueManager.aqmDequeueOk(nextQueueId, packet, ecn=True)
                            return packet
                        else: 
                            self.dropList.append({'time': time.time(), 'dropQueue': nextQueueId, 'dropState': 'AQM Dequeue'})
                            self.queueManager.aqmDequeueDrop(nextQueueId, packet)
                            continue
