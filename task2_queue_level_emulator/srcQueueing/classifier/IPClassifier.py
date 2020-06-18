from Classifier import Classifier

class IPClassifier(Classifier):

    def getQueueId(self, packet):
        if packet.getIPv4DstAddress() == ip2int('10.0.3.2'):
            return 1
        return 0
