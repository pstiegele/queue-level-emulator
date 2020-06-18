import argparse
import os, sys
import json
from scapy.all import *

import matplotlib
if "DISPLAY" not in os.environ:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scapy.utils import hexdump
from scapy.all import *

import numpy as np

noTitle = False

def parse_pcap_trace(pathIn, pathOut):
    packets_in = rdpcap(pathIn)
    packets_out = rdpcap(pathOut)
    out_pointer = 0
    #print("number ingoing packets: "+str(len(packets_in)))
    #print("number outgoing packets: "+str(len(packets_out)))
    resLst = []
    length = len(packets_out)
    dropLst = []
    basePacket = packets_in[0]
    counterDrops = 0
    for packet in packets_in:
        if (length == out_pointer):
            break
        out_packet = packets_out[out_pointer]
        tcp_in = packet['TCP']
        tcp_out = out_packet['TCP']
        match = tcp_in.seq == tcp_out.seq
        if(match):
            out_pointer+=1
            if len(packet) > 500:
                resLst.append((packet, out_packet))
        else:
            counterDrops = counterDrops + 1
            #print("Packet dropped: " + str(packet.time - basePacket.time))
            dropLst.append(packet)
    #print("number drops: " + str(counterDrops))
    print("number matched packets: "+str(len(resLst)))
    return packets_in, resLst


def plotPcapTrace(trace, out):
    plt.figure(1)
    fig = plt.gcf()
    fig.canvas.set_window_title('Pcap Trace')
    plt.subplot(211)

    x_values = []
    y_values = []
    basetime = trace[0][0].time
    for tuple in trace:
        a = tuple[0]
        b = tuple[1]
        diff = (b.time - a.time)*1000.0
        x_val = (a.time - basetime)
        y_val = diff
        x_values.append(x_val)
        y_values.append(y_val)
    plt.plot(x_values, y_values)
    plt.ylim(ymin = 0)
    plt.ylabel('delay [ms]')
    # plt.xlabel('time [s]')
    ax = plt.gca()
    ax.set_xticklabels([])

    plt.subplot(212)
    x_values = []
    y_values = []
    basetime = trace[0][0].time
    lastPacket = None
    for tuple in trace:
        outPacket = tuple[1]
        if lastPacket != None:
            diff = (outPacket.time - lastPacket.time)
            x_val = (outPacket.time - basetime)
            #print("Size: " + str(len(outPacket)) + " Diff: " + str(diff))
            y_val = (len(outPacket) * 0.008) / diff
            if y_val > 30000:
                lastPacket = outPacket
                print("Size: " + str(len(outPacket)) + " Diff: " + str(diff) + " Value: " + str(y_val))
                continue            
            x_values.append(x_val)
            y_values.append(y_val)
        lastPacket = outPacket
    #p = []
    #n = 10
    #for i in range(0, n):
    #    p.append(trace[0][1])
    #i = 0.0
    #for tuple in trace:
    #    i += 1
    #    p[n - 1] = tuple[1]
    #    if (i < n):
    #        diff = (p[n - 1].time - p[0].time) / i  # error correction for the n first entries
    #    else:
    #        diff = (p[n - 1].time - p[0].time) / n  # microseconds per packet
    #    x_val = (p[n - 1].time - basetime)
    #    if diff == 0:
    #        y_val = 0
    #    else:
    #        y_val = (len(p[n - 1]) * 0.008) / diff
    #    x_values.append(x_val)
    #    y_values.append(y_val)
    #    for j in range(0, n - 1):
    #        p[j] = p[j + 1]
    plt.plot(x_values, y_values)
    plt.ylim(ymin = 0)
    plt.ylabel('throughput [kbit/s]')
    plt.xlabel('time [s]')
    if not noTitle:
        plt.suptitle('pcap analysis')
    fig = plt.gcf()
    fig.set_size_inches(6, 3, forward=True)
    plt.savefig(out, bbox_inches='tight')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create matplot graph of pcap')
    parser.add_argument('--pathIn', type=str , default="out/in.pcap", action='store',  help='path to pcap in')
    parser.add_argument('--pathOut', type=str , default="out/out.pcap", action='store',  help='path to pcap out')
    parser.add_argument('--out', type=str , default="out/pcapTrace.pdf", action='store',  help='path to output pdf')
    args = parser.parse_args()
    pcap_in, pcap = parse_pcap_trace(args.pathIn, args.pathOut)
    plotPcapTrace(pcap, args.out)
