from QueueingSystem import QueueingSystem
from queue.PacketQueue import *
from queue.VirtualQueue import *
from Packet import *
from ratelimiter.Tokenbucket import Tokenbucket
from aqm.RED import RED
from aqm.CoDel import CoDel
from utils.jhash import lookup3
from utils.utils import *
import time, sys
import random

rate = 10*1000*1000/8 #1 = 1 byte per second
queue_depth = rate * 0.5#0.05
MTU = 1514
burstRate = 5000

ECN = False

# TODO at the moment only round robin packet wise and not byte wise

class FQQueueingSystem(QueueingSystem):
    '''
        This is a Stochastic Fair Queueing System. For fq_codel and fq_pie this type of fq is used.
        Their also exists a Strict Fair Queuing algorithm.

    '''
    def __init__(self, numberQueues=1024):
        self.salt = random.SystemRandom().randint(0, 4294967295)
        self.queues = dict() # Red black tree is the best data structure for Stochastic Fair Queueing 
        self.numberQueues = numberQueues
        self.dropList = []
        self.last_scheduled_queue = 0

        self.vQueue = VirtualQueue('vQueue', rateLimiter=Tokenbucket(rate, MTU, burstRate), depthBytes=queue_depth*self.numberQueues)#, 

        for x in range (0, numberQueues):
            self.queues[x] = PacketQueue(str(x), rateLimiter=None, depthBytes=queue_depth, aqm=CoDel(queueName=str(x)), parentQueue=self.vQueue)
    

    def getQueueId(self, packet):
        # FQ_CoDel uses Jenkins Hash lookup3 with the tuple(IP Protocol, IP Source, IP Dest, Src Port, Dst Port)
        ip_prot = packet.getIPv4Protocol()
        ip_src = packet.getIPv4SrcAddressRaw()
        ip_dst = packet.getIPv4DstAddressRaw()
        # TODO Only TCP support at the moment
        port_src = packet.getTCPSrcPort()
        port_dst = packet.getTCPDstPort()
        return ((lookup3(ip_prot + ip_src + ip_dst + port_src + port_dst) % self.numberQueues) + self.salt) % self.numberQueues     
    
    def insertPacket(self, packet):
        self.insertPacketTailDrop(packet)
        
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


    def logDrop(self):
        with open('out/dropped.json', 'w') as outfile:
            json.dump(self.dropList, outfile)
            

    def log(self):
        self.logDrop()
        #self.vQueue.log()
        for x in range(0, self.numberQueues):
            self.queues[x].log()
