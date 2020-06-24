
class Scheduler(object):
    """
    AQM is useful for buffering the incomming packets. Similarly, the scheduler is useful for
    buffering the outgoing packet, since the transmission rate might be less than the processing rate.
    User A---Input---Inputbuffer---switch processing time---Outputbuffer---Output---UserB 
    Typical Scheduler: FIFO, Round Robin, Fair Queue
    """
    def __init__(self, queueManager):
        self.queueManager = queueManager

    def nextQueueId(self):
        '''
            Get the next non-empty queue Id

            PROBLEM: What if packet will not be sent?
            Three cases exist:
            1. Packet will be sent or ECN mark but sent -> head of queue and reduced quantum
            2. Packet removed due to AQM -> head of queue and same quantum
            3. Rate limiter doesn't allow sending -> Not clear
            3.1. head of queue and same quantum (Like fq_codel because we assume only one rate limiter in the vQueue)
                If we have also rate limiter in real queues, the lowest rate limit blocks all other flows but fair share
            3.2. tail of queue and same quantum (We don't want starvation of the other queues)
                This results in a unfair share if we only have one rate limiter in the vQueue    
        '''
        raise NotImplementedError( "Concrete class should have implemented this." )

