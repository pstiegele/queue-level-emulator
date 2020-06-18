

class AQM(object):

    def enqueue(self, queue_size, packet):
        raise NotImplementedError( "Concrete class should have implemented this." )

    def dequeueOk(self, queue_size, packet, ecn=False):
        '''
            Only if the packet will be send to the interface
            AQM must check whether canDequeue was True or False 
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )

    def canDequeue(self, queue_size, packet):
        '''
            True if aqm is ok, otherwise False
            It's not allowed to change the state of the aqm in this function
        '''    
        raise NotImplementedError( "Concrete class should have implemented this." )

    def dequeueDrop(self, queue_size, packet):
        ''' 
            Only if packet will be dropped
            AQM must check whether canDequeue was True or False 
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )        

    def log(self):
        raise NotImplementedError( "Concrete class should have implemented this." )
