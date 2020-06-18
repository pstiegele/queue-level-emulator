from queuemanager.FQQueueManager import FQQueueManager
from classifier.FQClassifier import FQClassifier
from scheduler.RoundRobin import RoundRobin
from scheduler.DRR import DRR
from scheduler.FQScheduler import FQScheduler
from enqueuemanager.EnqueueManagerTailDrop import EnqueueManagerTailDrop
from enqueuemanager.FQEnqueueManagerFrontDropLong import FQEnqueueManagerFrontDropLong
from dequeuemanager.DequeueManager import DequeueManager
import json

class QueueingSystem(object):

    def __init__(self, queueManagerDescription='', systemDescription=''):
        ECN = False
        self.queueManager = FQQueueManager()
        scheduler = FQScheduler(self.queueManager, 400)
        #scheduler = RoundRobin(self.queueManager)
        #scheduler = DRR(self.queueManager, 400)
        classifier = FQClassifier(self.queueManager, scheduler)
        #classifier = FQClassifier(self.queueManager)
        #self.enqueueManager = EnqueueManagerTailDrop(self.queueManager, classifier, ECN)
        self.enqueueManager = FQEnqueueManagerFrontDropLong(self.queueManager, classifier, ECN)
        self.dequeueManager = DequeueManager(self.queueManager, scheduler, ECN)
        
    
    def callDequeueScheduler(self):       
        return self.dequeueManager.getPacket()
       
    
    def insertPacket(self, packet):
        self.enqueueManager.insertPacket(packet)

    def log(self):
        self.queueManager.log()
        dropList = self.enqueueManager.getLog() + self.dequeueManager.getLog()
        dropList = sorted(dropList, key=lambda ob: ob['time'])
        with open('out/dropped.json', 'w') as outfile:
            json.dump(dropList, outfile)