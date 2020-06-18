from EnqueueManager import EnqueueManager
from utils.utils import *
import time

class EnqueueManagerTailDrop(EnqueueManager):

    def insertPacket(self, packet):
        queueId = self.classifier.getQueueId(packet)
        resCode = self.queueManager.canPush(queueId, packet)
        if resCode == 0:
            self.queueManager.push(queueId, packet)
        else:
            # VQueue full
            if getBitAtPosition(resCode, 1) == 1:
                packet.setDropped()       
                self.dropList.append({'time': time.time(), 'dropQueue': queueId, 'dropState': 'Tail'})
            # Only Own Queue full
            elif getBitAtPosition(resCode, 0) == 1:
                packet.setDropped()        
                self.dropList.append({'time': time.time(), 'dropQueue': queueId, 'dropState': 'Tail'})
            # AQM drop            
            elif getBitAtPosition(resCode, 2) == 1:
                if self.ECN and packet.hasECN():
                    self.dropList.append({'time': time.time(), 'dropQueue': queueId, 'dropState': 'AQM Enqueue ECN'})
                    packet.ecnMark()
                    self.queueManager.push(queueId, packet)                    
                else:
                    packet.setDropped()       
                    self.dropList.append({'time': time.time(), 'dropQueue': queueId, 'dropState': 'AQM Enqueue'})
