

class Classifier(object):

    def __init__(self, queueManager):
        self.queueManager = queueManager

    def getQueueId(self, packet):
        '''
            Returns the queue Id of the given packet
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )
