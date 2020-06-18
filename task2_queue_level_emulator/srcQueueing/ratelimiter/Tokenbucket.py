import time
from RateLimiter import RateLimiter

class Tokenbucket(RateLimiter):
    
    def __init__(self, rate, mtu, burstRate):
        self.rate = rate
        self.MTU = mtu
        self.burstRate = burstRate
        self.token = [time.time(), 0]


    def update(self):
        delta_t = time.time() - self.token[0]
        new_buckets = delta_t*self.rate

        if(new_buckets > 0):
            newTokens = self.token[1] + new_buckets
            if newTokens > self.burstRate:
                newTokens = self.burstRate
            self.token[1] = newTokens
            self.token[0] = time.time()
    
    def canSendPacket(self):
        self.update()
        return self.token[1] >= self.MTU

    def packetSent(self, packet):
        self.token[1] = self.token[1] - packet.getSize()
