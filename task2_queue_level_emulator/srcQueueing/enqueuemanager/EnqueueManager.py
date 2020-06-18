

class EnqueueManager(object):

    def __init__(self, queueManager, classifier, ECN=False):
        self.queueManager = queueManager
        self.classifier = classifier
        self.ECN = ECN
        self.dropList = []

    def insertPacket(self, packet):
        '''
            Insert packet into the queueing system
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )

    def getLog(self):
        return self.dropList
