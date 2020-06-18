#!/usr/bin/python
from scapy.all import *
from Packet import Packet
from queueingsystem.SimpleQueueingSystem import *
from queueingsystem.RateLimitedQueueingSystem import *
from queueingsystem.VQRateLimitedQueueingSystem import *
from queueingsystem.FQQueueingSystem import *
from queueingsystem.QueueingSystem import *
from utils.utils import *
import datetime
import time
from threading import *
from multiprocessing import Process
import sys
from socket import socket, AF_PACKET, SOCK_RAW, htons
from binascii import hexlify
import subprocess
import os.path


inf0 = 'bng-eth0'
inf1 = 'bng-eth1'

client_ip = ip2int('10.0.0.2')
def filt0(p): return p.getIPv4SrcAddress() == client_ip
def filt1(p): return p.getIPv4SrcAddress() != client_ip


def main():
    print("Start Queueing Runner ")
    p1 = Process(target=createProcess1)
    p2 = Process(target=createProcess2)

    p1.start()
    p2.start()


def createProcess1(): # packets from eth0 to eth1
    
    #queueingSystem = RateLimitedQueueingSystem(2)
    #queueingSystem = SimpleQueueingSystem()
    #queueingSystem = VirtualQueueRateLimitedQueueingSystem(2)
    #queueingSystem = FQQueueingSystem()
    queueingSystem = QueueingSystem()
    Thread(target=startSniffing, args=[queueingSystem, inf0, filt0, "10.0.1.2"]).start()
    Thread(target=popQueue, args=[queueingSystem, inf1]).start()
    while not os.path.isfile("stopQueueingRunner") :
        time.sleep(0.5)
    queueingSystem.log()

def createProcess2(): # packets from eth1 to eth0
    queueingSystem = SimpleQueueingSystem()
    Thread(target=startSniffing, args=[queueingSystem, inf1, filt1, "10.0.0.2"]).start()
    Thread(target=popQueue, args=[queueingSystem, inf0]).start()
    while not os.path.isfile("stopQueueingRunner") :
        time.sleep(0.5)

def startSniffing(queueingSystem, iface, filt, next_hop_ip):
    print("Start Sniffing " + str(os.getpid()) + " " + str(currentThread()) )
    sys.stdout.flush()
    sock = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL))
    sock.bind((iface, 0))

    own_mac = get_if_hwaddr(iface)
    own_mac = own_mac.replace(":", "")
    own_mac = own_mac.decode("hex")
    next_hop_mac = gettingMac(next_hop_ip)   

    while True:
        receivedPacket = sock.recv(2048)
        p = Packet(receivedPacket)
        if p.getEthertype() == "0800":
            if filt(p):
                p.setMac(own_mac, next_hop_mac) 
                queueingSystem.insertPacket(p)
      

def popQueue(queueingSystem, iface):
    print("Start dequeueing "+ str(os.getpid()) + " " + str(currentThread()) )
    sock = socket(AF_PACKET, SOCK_RAW)
    sock.bind((iface, 0))
    print("bind dequeing to interface: "+ iface)
    sys.stdout.flush()
    
    packet = None
    while True:
        if(packet != None):
            try:
                sock.send(bytes(packet.getData()))      
                #TODO remove data from packet construct       
                packet = queueingSystem.callDequeueScheduler()
            except:
                time.sleep(0.0001)
        else:
            time.sleep(0.0001)            
            packet = queueingSystem.callDequeueScheduler()



if __name__ == '__main__':
    main()

