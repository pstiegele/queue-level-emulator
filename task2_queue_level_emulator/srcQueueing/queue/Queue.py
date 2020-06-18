from Packet import *
import time
import json
import sys
from utils.utils import *
from threading import Lock, Thread

class Queue(object):
    def __init__(self, name=None, rateLimiter=None, depthBytes=0xFFFFFFFFFFFFFFFF, aqm=None, parentQueue=None):        
        self.maxSize = depthBytes        
        self.byte_len = 0
        self.pkt_len = 0
        self.log_lst = []
        self.logQ()
        self.name = name
        self.lock = Lock()
        self.rateLimiter = rateLimiter
        self.aqm = aqm
        self.parentQueue = parentQueue

    def log(self):
        if self.name == None or len(self.log_lst) <= 1:
            return
        with open('out/queue'+self.name+'.json', 'w') as outfile:
            json.dump({'maxDepth': self.maxSize, 'list': self.log_lst}, outfile)
        if self.aqm != None:
            self.aqm.log()

    def canPush(self, packet):
        """ return 0000 = Ok, 0001 = Own Queue Full, 0010 = Parent(s) Queue Full, 0100 = Own or Parent(s) AQM Drop
        """
        returnCode = 0
        if self.byte_len + packet.getSize() > self.maxSize:
            returnCode = returnCode | int('0b1', 2)        
        if self.parentQueue != None:
            parentCode = self.parentQueue.canPush(packet)
            if parentCode != 0:
                if getBitAtPosition(parentCode, 0) == 1 or getBitAtPosition(parentCode, 1) == 1:
                    returnCode = returnCode | int('0b10', 2)
                if getBitAtPosition(parentCode, 2) == 1:
                    returnCode = returnCode | int('0b100', 2)
        if self.aqm != None and self.aqm.enqueue(self.byte_len, packet):
            returnCode = returnCode | int('0b100', 2)
        return returnCode

    def push(self, packet):      
        self.lock.acquire()
        self.byte_len += packet.getSize()
        self.pkt_len += 1
        self.logQ()
        self.lock.release()
        if self.parentQueue != None:
            self.parentQueue.push(packet)
        

    def canPop(self, packet):
        """ return 0000 = Ok, 0001 = Own Queue Empty, 0010 = Parent(s) Queue Empty, 
            0100 = Own or Parent(s) Rate Limiter Not Allowed, 1000 = Own or Parent(s) AQM Drop
        """   
        returnCode = 0
        if self.pkt_len == 0:
            returnCode = returnCode | int('0b1', 2)
        if self.rateLimiter != None and not self.rateLimiter.canSendPacket():
            returnCode = returnCode | int('0b100', 2)
        if self.parentQueue != None:
            parentCode = self.parentQueue.canPop(packet)
            if parentCode != 0:
                if getBitAtPosition(parentCode, 0) == 1 or getBitAtPosition(parentCode, 1) == 1:
                    returnCode = returnCode | int('0b10', 2)
                if getBitAtPosition(parentCode, 2) == 1:
                    returnCode = returnCode | int('0b100', 2)
                if getBitAtPosition(parentCode, 3) == 1:
                    returnCode = returnCode | int('0b1000', 2)    
        if self.aqm != None and not self.aqm.canDequeue(self.byte_len, packet):
            returnCode = returnCode | int('0b1000', 2)
        return returnCode
 

    def pop(self, packet, drop=False):  
        self.lock.acquire()     
        self.byte_len -= packet.getSize()
        self.pkt_len -= 1        
        self.logQ()
        self.lock.release()
        if self.parentQueue != None:
            self.parentQueue.pop(packet, drop)
        if self.rateLimiter != None and not drop:
            self.rateLimiter.packetSent(packet)

    def rateLimiterSend(self, packet):
        if self.parentQueue != None:
            self.parentQueue.rateLimiterSend(packet)
        if self.rateLimiter != None:
            self.rateLimiter.packetSent(packet)

    def aqmDequeueOk(self, packet, ecn=False):
        if self.parentQueue != None:
            self.parentQueue.aqmDequeueOk(packet, ecn)
        if self.aqm != None:
            self.aqm.dequeueOk(self.byte_len, packet, ecn)

    def aqmDequeueDrop(self, packet):
        if self.parentQueue != None:
            self.parentQueue.aqmDequeueDrop(packet)
        if self.aqm != None:
            self.aqm.dequeueDrop(self.byte_len, packet)                

    def getByteLength(self):
        return self.byte_len

    def getPaketLength(self):
        return self.pkt_len

    def logQ(self):
        self.log_lst.append((time.time(), self.byte_len, self.pkt_len))

    def getRateLimiter(self):
        return self.rateLimiter

    def getAQM(self):
        return self.aqm

    def getParentQueue(self):
        return self.parentQueue
