from EnqueueManager import EnqueueManager
from utils.utils import *
import time

class EnqueueManagerFrontDrop(EnqueueManager):

    def insertPacket(self, packet):
        queueId = self.classifier.getQueueId(packet)
        resCode = self.queueManager.canPush(queueId, packet)
        if resCode == 0:
            self.queueManager.push(queueId, packet)
        else:
            # Own queue full
            if getBitAtPosition(resCode, 0) == 1:
                pOld = self.queueManager.pop(queueId, drop=True)
                pOld.setDropped()  
                self.queueManager.push(queueId, packet)
                self.dropList.append({'time': time.time(), 'dropQueue': queueId, 'dropState': 'Front'})
            # Only VQueue full
            elif getBitAtPosition(resCode, 1) == 1:
                packet.setDropped()       
                self.dropList.append({'time': time.time(), 'dropQueue': queueId, 'dropState': 'Front'})
            # AQM drop            
            elif getBitAtPosition(resCode, 2) == 1:
                if self.ECN and packet.hasECN():
                    self.dropList.append({'time': time.time(), 'dropQueue': queueId, 'dropState': 'AQM Enqueue ECN'})
                    slef.queueManager.markEcnFirstPacket(queueId)
                    self.queueManager.push(queueId, packet)                    
                else:
                    pOld = self.queueManager.pop(queueId, drop=True)
                    pOld.setDropped()  
                    self.queueManager.push(queueId, packet)       
                    self.dropList.append({'time': time.time(), 'dropQueue': queueId, 'dropState': 'AQM Enqueue'})

