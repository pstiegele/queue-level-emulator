from Packet import *
import time
import json
import sys
from threading import Lock, Thread
from collections import deque
from Queue import Queue

class PacketQueue(Queue):
    def __init__(self, name=None, rateLimiter=None, depthBytes=0xFFFFFFFFFFFFFFFF, aqm=None, parentQueue=None):
        super(PacketQueue, self).__init__(name=name, rateLimiter=rateLimiter, depthBytes=depthBytes, aqm=aqm, parentQueue=parentQueue)        
        self.packetList = deque()        

    def push(self, packet):      
        self.packetList.append(packet)
        packet.setEnqueueTimestamp(time.time())
        super(PacketQueue, self).push(packet)

    def canTailPop(self):
        if len(self.packetList) > 0:
            p = self.packetList[-1] # Last element
            return super(PacketQueue, self).canPop(p)
        return 1

    def canPop(self):
        if len(self.packetList) > 0:
            p = self.packetList[0] # First element
            return super(PacketQueue, self).canPop(p)
        return 1        

    def tailpop(self, drop=False):
        p = self.packetList.pop()
        p.setDequeueTimestamp(time.time())
        super(PacketQueue, self).pop(p, drop)
        return p

    def pop(self, drop=False):
        p = self.packetList.popleft()
        p.setDequeueTimestamp(time.time())
        super(PacketQueue, self).pop(p, drop)
        return p
    
    def markEcnFirstPacket(self):
        p = self.packetList.popleft()
        p.ecnMark()
        self.packetList.appendleft(p)

    def sizeOfFirstPacket(self):
        p = self.packetList.popleft()
        size = p.getSize()
        self.packetList.appendleft(p)
        return size        
