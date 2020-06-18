import struct

class Packet:
    def __init__(self, data):
        self.data = data
        self.size = len(data)
        self.dropped = False

    def getData(self):
        return self.data

    def getSize(self):
        return self.size

    def setEnqueueTimestamp(self, time):
        self.enqueueTime = time

    def getEnqueueTimestamp(self):
        return self.enqueueTime
    
    def setDequeueTimestamp(self, time):
        self.dequeueTime = time

    def getDequeueTimestamp(self):
        return self.dequeueTime
        
    def getQueueDelay(self):
        return self.dequeueTime - self.enqueueTime

    def setDropped(self):
        self.dropped = True

    def isDropped(self):
        return self.dropped

    def getIPv4Protocol(self):
        return self.data[23]  
    def getTCPSrcPort(self):
        return self.data[34:36]
    def getTCPDstPort(self):
        return self.data[36:38]
    def getIPv4SrcAddressRaw(self):
        return self.data[26:30]
    def getIPv4DstAddressRaw(self):
        return self.data[30:34]    
    def setMac(self, newSrcMac, newDstMac):
        self.data = newDstMac + newSrcMac + self.data[12:]
    def getEthertype(self):
        return (self.data[12:14]).encode("hex")
    def getIPv4SrcAddress(self):
        return int((self.data[26:30]).encode("hex"), 16)
    def getIPv4DstAddress(self):
        return int((self.data[30:34]).encode("hex"), 16)
    def hasECN(self):
        return int(self.data[15].encode("hex"), 16) == 2
    def ecnMark(self):
        if int(self.data[15].encode("hex"), 16) == 2:
            #Update Checksum
            # TODO only working for 10 -> 11 not 01 -> 11
            checksum = self.data[24:26]
            intC = int(checksum.encode("hex"), 16) - 1
            newCkSum = struct.pack(">H", intC & 65535)
            #Set bit
            self.data = self.data[0:15] + "\03" + self.data[16:24] + newCkSum + self.data[26:]
            
