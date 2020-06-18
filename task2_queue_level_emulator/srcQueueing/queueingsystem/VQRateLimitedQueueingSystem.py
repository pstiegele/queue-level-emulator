from QueueingSystem import QueueingSystem
from queue.PacketQueue import *
from queue.VirtualQueue import *
from Packet import *
from ratelimiter.Tokenbucket import Tokenbucket
from aqm.RED import RED
from aqm.CoDel import CoDel
from aqm.BasicPIE import BasicPIE
from aqm.EnhancementPIE import EnhancementPIE
from aqm.LinuxPIE import LinuxPIE
from utils.utils import *
import time, sys

rate = 10*1000*1000/8 #1 = 1 byte per second
queue_depth = rate * 0.1#0.05
MTU = 1514
burstRate = 5000

ECN = False

class VirtualQueueRateLimitedQueueingSystem(QueueingSystem):
    def __init__(self, numberQueues):
        self.queues = dict()
        self.numberQueues = numberQueues
        self.dropList = []
        self.last_scheduled_queue = 0

        self.vQueue = VirtualQueue('vQueue', rateLimiter=Tokenbucket(rate*1.5, MTU, burstRate*1.5), depthBytes=queue_depth*1.5)#, aqm=CoDel('vQueue'))#aqm=RED(queueName='vQueue',queue_depth_bytes=queue_depth*0.8, rateLimiterBW=rate*0.8))

        for x in range (0, numberQueues):
            self.queues[x] = PacketQueue(str(x), rateLimiter=Tokenbucket(rate, MTU, burstRate), depthBytes=queue_depth, aqm=RED(queueName=str(x),queue_depth_bytes=queue_depth, rateLimiterBW=rate))#, parentQueue = self.vQueue,)

    def getQueueId(self, packet):
        #if packet.getIPv4DstAddress() == ip2int('10.0.3.2'):
        #    return 1
        return 0
        #return packet.getIPv4DstAddress() % self.numberQueues
    
    def insertPacket(self, packet):
        self.insertPacketTailDrop(packet)
        #self.insertPacketFrontDropLong(packet)
        #self.insertPacketTailDropLong(packet)

    def insertPacketFrontDropLong(self, packet):
        queueId = self.getQueueId(packet)
        resCode = self.queues[queueId].canPush(packet)
        # VQueue full
        if getBitAtPosition(resCode, 1) == 1:
            # Drop front longest queue, but from queueId if it's one of the longest 
            longestQueue = self.getLongestQueue(queueId)
            pOld = self.queues[longestQueue].pop(drop=True)
            pOld.setDropped()          
            self.dropList.append({'time': time.time(), 'dropQueue': longestQueue, 'dropState': 'Front'})
        # Only Own Queue full
        elif getBitAtPosition(resCode, 0) == 1:
            pOld = self.queues[queueId].pop(drop=True)
            pOld.setDropped()          
            self.dropList.append({'time': time.time(), 'dropQueue': queueId, 'dropState': 'Front'})
        # AQM drop            
        elif getBitAtPosition(resCode, 2) == 1:
            pOld = self.queues[queueId].pop(drop=True)
            pOld.setDropped()          
            self.dropList.append({'time': time.time(), 'dropQueue': queueId, 'dropState': 'AQM Enqueue'})
        self.queues[queueId].push(packet)     
        
    def insertPacketTailDrop(self, packet):
        queueId = self.getQueueId(packet)
        resCode = self.queues[queueId].canPush(packet)
        if resCode == 0:
            self.queues[queueId].push(packet)
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
                if ECN and packet.hasECN():
                    self.dropList.append({'time': time.time(), 'dropQueue': queueId, 'dropState': 'AQM Enqueue ECN'})
                    packet.ecnMark()
                    self.queues[queueId].push(packet)                    
                else:
                    packet.setDropped()       
                    self.dropList.append({'time': time.time(), 'dropQueue': queueId, 'dropState': 'AQM Enqueue'})
                     

    def insertPacketTailDropLong(self, packet):
        queueId = self.getQueueId(packet)
        resCode = self.queues[queueId].canPush(packet)
        if resCode == 0:
            self.queues[queueId].push(packet)
        else:
            # Own Queue full
            if getBitAtPosition(resCode, 0) == 1:
                packet.setDropped()       
                self.dropList.append({'time': time.time(), 'dropQueue': queueId, 'dropState': 'Tail'})
            # VQueue full
            elif getBitAtPosition(resCode, 1) == 1:
                # Drop front longest queue, must be different to queueId 
                longestQueue = self.getLongestQueue(queueId)
                pOld = self.queues[longestQueue].tailpop(drop=True)
                pOld.setDropped()          
                self.dropList.append({'time': time.time(), 'dropQueue': longestQueue, 'dropState': 'Tail'})
                self.queues[queueId].push(packet)
            # AQM drop            
            elif getBitAtPosition(resCode, 2) == 1:
                packet.setDropped()               
                self.dropList.append({'time': time.time(), 'dropQueue': queueId, 'dropState': 'AQM Enqueue'})        

    def callDequeueScheduler(self):
        if(self.last_scheduled_queue == self.numberQueues):
            self.last_scheduled_queue = 0
        else:
            self.last_scheduled_queue += 1
        for q in range(self.last_scheduled_queue, self.numberQueues) + range(0, self.last_scheduled_queue):
            resCode = self.queues[q].canPop()
            if resCode == 0:            
                packet = self.queues[q].pop()
                self.last_scheduled_queue = q
                self.queues[q].aqmDequeueOk(packet)
                return packet
            if getBitAtPosition(resCode, 2) == 1: # RateLimiter not OK
                continue    
            if getBitAtPosition(resCode, 3) == 1: # AQM not OK   
                if not ECN:
                    packet = self.queues[q].pop(drop=True)
                    self.last_scheduled_queue = q               
                    self.dropList.append({'time': time.time(), 'dropQueue': q, 'dropState': 'AQM Dequeue'})
                    self.queues[q].aqmDequeueDrop(packet)
                    return None
                elif getBitAtPosition(resCode, 2) == 0:
                    packet = self.queues[q].pop(drop=True) # True doesn't change rate limiter must be set manually
                    self.last_scheduled_queue = q
                    if packet.hasECN():
                        self.queues[q].rateLimiterSend(packet)
                        self.dropList.append({'time': time.time(), 'dropQueue': q, 'dropState': 'AQM Dequeue ECN'})
                        packet.ecnMark()
                        self.queues[q].aqmDequeueOk(packet, ecn=True)
                        return packet
                    else: 
                        self.dropList.append({'time': time.time(), 'dropQueue': q, 'dropState': 'AQM Dequeue'})
                        self.queues[q].aqmDequeueDrop(packet)
                        return None
        return None

    def getLongestQueue(self, currentQueue):
        size = 0
        index = 0
        for q in range(0, self.numberQueues):
            currentByteLength = self.queues[q].getByteLength()
            if currentByteLength > size or (currentByteLength == size and q == currentQueue):
                size = self.queues[q].getByteLength()
                index = q
        return index

    def logDrop(self):
        with open('out/dropped.json', 'w') as outfile:
            json.dump(self.dropList, outfile)
            

    def log(self):
        self.logDrop()
        self.vQueue.log()
        for x in range(0, self.numberQueues):
            self.queues[x].log()
