from QueueingSystem import QueueingSystem
from queue.PacketQueue import *
from Packet import *
import time

###################################
# 1 queue system without rate limiting
###################################
class SimpleQueueingSystem(QueueingSystem):
    def __init__(self):
        self.queue = PacketQueue()
        self.sentPackets = []
        
    def callDequeueScheduler(self):
        if self.queue.canPop() == 0:
            packet = self.queue.pop()
            return packet
        return None        
    
    def insertPacket(self, packet):
        if self.queue.canPush(packet) == 0:        
            self.queue.push(packet)
        else:
            packet.setDropped()

    def getSentPackets(self, queueId):
        return self.sentPackets[queueId]
