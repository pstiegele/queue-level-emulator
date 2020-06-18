
class RateLimiter(object):

    def update(self):
        '''
            Update the current rate limiter.
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )
    
    def canSendPacket(self):
        '''
            Returns True if it's okay to send a packet
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )

    def packetSent(self, packet):
        '''
            Notify the rate limiter that a packet was sent.
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )
