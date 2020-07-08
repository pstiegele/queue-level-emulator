import matplotlib
import os
if "DISPLAY" not in os.environ:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scapy.utils import hexdump
from scapy.all import *
import numpy as np
import json


def parse_iperf3_json(path):
    file = open(path, "r")
    content = file.read()
    content = json.loads(content)
    #now content is a dict
    loRawInputs = content['intervals']
    resLst = []
    for x in loRawInputs:
        innerLst = []
        for y in x['streams']:
            innerLst.append(y) #TODO hier wird nur der erste Stream geparst
        resLst.append(innerLst)
    print(resLst)
    return  resLst

def plotIperf3(raw_data):
    plt.figure(1)
    fig = plt.gcf()
    fig.canvas.set_window_title('IPerf3')
    plt.subplot(211)

    x_values = [0]
    y_values = [0]
    for data in raw_data:
        x_val = data[0]['start']
        y_val = 0
        for x in data:
            y_val += x['rtt']/1000.0
        y_val = y_val/len(data)
        x_values.append(x_val)
        y_values.append(y_val)
    plt.plot(x_values, y_values)
    plt.ylim(ymin = 0)
    plt.ylabel('RTT [ms]')
    ax = plt.gca()
    ax.set_xticklabels([])

    plt.subplot(212)
    x_values = [0]
    y_values = [0]
    for data in raw_data:
        x_val = data[0]['start']
        y_val = 0
        for x in data:
            y_val += x['bytes']*8 / x['seconds']
        y_val = y_val/1000
        x_values.append(x_val)
        y_values.append(y_val)
    plt.plot(x_values, y_values)
    plt.ylim(ymin = 0)
    plt.xlabel('time [s]')
    plt.ylabel('Throughput [kbits/s]')
    plt.suptitle('iperf3 json output')
    fig = plt.gcf()
    fig.set_size_inches(6, 3, forward=True)
    plt.savefig('iperf3.pdf', bbox_inches='tight')

res = parse_iperf3_json("iperf.json")
plotIperf3(res)
