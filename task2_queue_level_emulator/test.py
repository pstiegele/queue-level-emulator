#!/usr/bin/python
from scapy.all import *
#from kamene.all import *
import time
import datetime
import ctypes
from socket import socket, AF_PACKET, SOCK_RAW
import struct

from binascii import hexlify

class Packet:
    def __init__(self, data):
        self.data = data
        self.size = len(data)

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

    def setMac(self, newSrcMac, newDstMac):
        self.data = newDstMac + newSrcMac + self.data[12:]
    def getEthertype(self):
        return (self.data[12:14]).encode("hex")
    def getIPv4SrcAddress(self):
        return int((self.data[26:30]).encode("hex"), 16)





def ip2int(addr):
    return struct.unpack("!I", inet_aton(addr))[0]
print(ip2int("172.16.5.2"))
start = time.time()
sock = socket(AF_PACKET, SOCK_RAW)
sock.bind(("bng-eth0", 0))   
mac =  hexlify(sock.getsockname()[4])
#print(mac)
#for i in range(0,1000):

my_mac = "92:6e:37:b2:e3:b6"
my_mac = my_mac.replace(":", "")
my_mac = my_mac.decode("hex")
src_addr = "\x01\x02\x03\x04\x05\x06"
dst_addr = "\x01\x02\x03\x04\x05\x06"
payload = ("["*30)+"PAYLOAD"+("]"*30)
checksum = "\x1a\x2b\x3c\x4d"
ethertype = "\x08\x01"
packet = Packet(dst_addr+src_addr+ethertype+payload+checksum)
packet.setMac(my_mac, "\xff\xff\xff\xff\xff\xff")
for j in range (0, 1000):
    for i in range (0, 1000):
#    packet.setDequeueTimestamp(datetime.datetime.now())
#    print(packet.getData().encode("hex"))
        try:
            sock.send(bytes(packet.getData()))
        except:
            time.sleep(0.01)
#    print(packet.getData().encode("hex"))
#    print(packet.getEthertype())
#    print(int(packet.getIPv4Address(), 16))
    #sock.send(dst_addr+src_addr+ethertype+payload+checksum)
    
end = time.time()
#print(1000/(end - start))
