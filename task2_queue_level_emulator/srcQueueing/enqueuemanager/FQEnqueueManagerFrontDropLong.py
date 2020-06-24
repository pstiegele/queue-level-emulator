from EnqueueManager import EnqueueManager
from utils.utils import *
import time

class FQEnqueueManagerFrontDropLong(EnqueueManager):

    def insertPacket(self, packet):
        queueId = self.classifier.getQueueId(packet)
        resCode = self.queueManager.canPush(queueId, packet)
        # VQueue full
        if getBitAtPosition(resCode, 1) == 1:
            # Drop front longest queue, but from queueId if it's one of the longest 
            longestQueue = self.queueManager.getLongestQueue(queueId)
            # FQ removes half of the queue size or up to 64 from the longest queue if size of all queues reach limit
            halfQueueLength = self.queueManager.queueLength(longestQueue) / 2
            numPackets = min(halfQueueLength, 64)
            for i in range(0, numPackets):
                pOld = self.queueManager.pop(longestQueue, drop=True)
                pOld.setDropped()     
                self.dropList.append({'time': time.time(), 'dropQueue': longestQueue, 'dropState': 'Front'})
        # Only Own Queue full
        elif getBitAtPosition(resCode, 0) == 1:
            pOld = self.queueManager.pop(queueId, drop=True)
            pOld.setDropped()          
            self.dropList.append({'time': time.time(), 'dropQueue': queueId, 'dropState': 'Front'})
        # AQM drop
        # TODO ECN support            
        elif getBitAtPosition(resCode, 2) == 1:
            pOld = self.queueManager.pop(queueId, drop=True)
            pOld.setDropped()          
            self.dropList.append({'time': time.time(), 'dropQueue': queueId, 'dropState': 'AQM Enqueue'})
        self.queueManager.push(queueId, packet)                    
