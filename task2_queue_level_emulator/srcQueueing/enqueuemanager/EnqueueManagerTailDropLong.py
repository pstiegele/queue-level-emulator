from EnqueueManager import EnqueueManager
from utils.utils import *
import time

class EnqueueManagerTailDropLong(EnqueueManager):

    def insertPacket(self, packet):
        queueId = self.classifier.getQueueId(packet)
        resCode = self.queuemanager.canPush(queueId, packet)
        if resCode == 0:
            self.queueManager.push(queueId, packet)
        else:
            # Own Queue full
            if getBitAtPosition(resCode, 0) == 1:
                packet.setDropped()       
                self.dropList.append({'time': time.time(), 'dropQueue': queueId, 'dropState': 'Tail'})
            # VQueue full
            elif getBitAtPosition(resCode, 1) == 1:
                # Drop front longest queue, must be different to queueId 
                longestQueue = self.queueManager.getLongestQueue(queueId)
                pOld = self.queueManager.tailpop(longestQueue, drop=True)
                pOld.setDropped()          
                self.dropList.append({'time': time.time(), 'dropQueue': longestQueue, 'dropState': 'Tail'})
                self.queueManager.push(queueId, packet)
            # AQM drop
            # TODO ECN support            
            elif getBitAtPosition(resCode, 2) == 1:
                packet.setDropped()               
                self.dropList.append({'time': time.time(), 'dropQueue': queueId, 'dropState': 'AQM Enqueue'})  

