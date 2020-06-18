from Packet import *
import time
import json
import sys
from threading import Lock, Thread
from Queue import Queue

class VirtualQueue(Queue):
    def __init__(self, name=None, rateLimiter=None, depthBytes=0xFFFFFFFFFFFFFFFF, aqm=None, parentQueue=None):        
        super(VirtualQueue, self).__init__(name=name, rateLimiter=rateLimiter, depthBytes=depthBytes, aqm=aqm, parentQueue=parentQueue)
