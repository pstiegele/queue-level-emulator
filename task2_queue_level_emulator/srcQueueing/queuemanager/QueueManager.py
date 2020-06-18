
class QueueManager(object):

    def numQueues(self):
        '''
            Return number of queues
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )

    def followingQueueId(self, currentQueueId):
        '''
            Returns the next queueId after currentQueueId. 
            If currentQueueId is the last Id then return the first Id 
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )

    def previousQueueId(self, currentQueueId):
        '''
            Returns the previous queueId before currentQueueId. 
            If currentQueueId is the first Id then return the last Id 
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )

    def hasQueueData(self, queueId):
        '''
            Returns true if queue is not empty
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )

    def queueLength(self, queueId):
        '''
            Returns the size of the selected queue in packets
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )    

    def canPop(self, queueId):
        '''
            Returns canPop of the selected queue
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )

    def pop(self, queueId, drop=False):
        '''
            Calls pop on the selected queue
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )

    def aqmDequeueOk(self, queueId, packet, ecn=False):
        '''
            Calls aqmDequeueOk on the selected queue
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )

    def aqmDequeueDrop(self, queueId, packet):
        '''
            Calls aqmDequeueDrop on the selected queue
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )

    def rateLimiterSend(self, queueId, packet):
        '''
            Calls rateLimiterSend on the selected queue
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )

    def canPush(self, queueId, packet):
        '''
            Returns canPush of the selected queue
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )

    def push(self, queueId, packet):
        '''
            Calls push on the selected queue
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )

    def tailpop(self, queueId, drop=False):
        '''
            Calls tailpop on the selected queue
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )

    def getLongestQueue(self, queueId):
        '''
            Returns the longest queue of the queue manager. 
            If multiple are the longest and queueId is one of them return queueId.
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )

    def markEcnFirstPacket(self, queueId):
        '''
            Mark the first packet in the selected queue as ECN Drop 
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )

    def sizeOfFirstPacket(self, queueId):
        '''
            Return the size in bytes of the first packet in the selected queue
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )

    def log(self):
        '''
            logs the statistics of the queue
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )