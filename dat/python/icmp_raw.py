import struct
import socket
from checksum import checksum
from random import randint

def icmp():
    type = 8
    code=0
    chksum=0
    id=randint(0,0xFFFF)
    seq=1
    real_chksum= checksum(struct.pack("!BBHHH",type,code,chksum,id,seq))
    icmp_pkt=struct.pack("!BBHHH",type,code,socket.htons(real_chksum),id,seq)
    return icmp_pkt
h2_ip= "10.0.0.2"
h2_port=0
h2_address=(h2_ip,h2_port)
s=socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_ICMP)
s.sendto(icmp(),h2_address)
