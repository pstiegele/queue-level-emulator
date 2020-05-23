import struct
from socket import*
import threading
import time
from checksum import checksum
from random import randint

#ip= "10.0.0.2"
#port1 = 1
#port2=2

#ip_h3= "192.168.1.3"
#port_h3=1
#h3_address= (ip_h3,port_h3)

#ip_h1="10.0.0.1"
#port_h1=1
#h1_address=(ip_h1,port_h1)

listeningAddress_port1 = ("h2-eth0",0)
rawSocket= socket(AF_PACKET,SOCK_RAW,0x0300)    
rawSocket.bind(listeningAddress_port1)


listeningAddress_port2 = ("h2-eth1",0)
rawSocket_2= socket(AF_PACKET,SOCK_RAW,0x0300)
rawSocket_2.bind(listeningAddress_port2)

def _forwardtoH3():
    while(True):
        data,sourceAddress= rawSocket.recvfrom(4096)
        #print("Data received from '{0}'".format(sourceAddress[0]))
        rawSocket.sendto(data,("h2-eth1",0))
        #print("Forward Packet to h3")

def _forwardtoH1():
    while(True):
        data2,sourceAddress2= rawSocket_2.recvfrom(4096)
        #print("Data received from '{0}'".format(sourceAddress2[0]))
        rawSocket.sendto(data2,("h2-eth0",0))
        #print("Forward Packet to h1")
t1=threading.Thread(target=_forwardtoH3,name='t1')
t2=threading.Thread(target=_forwardtoH1,name='t2')
t1.start()
t2.start()



