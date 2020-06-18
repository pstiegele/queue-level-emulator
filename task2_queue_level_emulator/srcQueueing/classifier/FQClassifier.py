from Classifier import Classifier
from utils.jhash import lookup3
import random

class FQClassifier(Classifier):

    def __init__(self, queueManager, fqScheduler=None):
        super(FQClassifier, self).__init__(queueManager)
        self.salt = random.SystemRandom().randint(0, 4294967295)
        self.fqScheduler = fqScheduler # Must be the FQScheduler because it has additional methods

    def getQueueId(self, packet):
        numQueues = self.queueManager.numQueues()
        ip_prot = packet.getIPv4Protocol()
        ip_src = packet.getIPv4SrcAddressRaw()
        ip_dst = packet.getIPv4DstAddressRaw()
        # TODO Only TCP support at the moment
        port_src = packet.getTCPSrcPort()
        port_dst = packet.getTCPDstPort()
        queueId = ((lookup3(ip_prot + ip_src + ip_dst + port_src + port_dst) % numQueues) + self.salt) % numQueues
        if self.fqScheduler != None:
            self.fqScheduler.queueClassified(queueId)
        return queueId

