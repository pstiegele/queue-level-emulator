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

def plotIperf3(raw_data, raw_data2):
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

    x2_values = [0]
    y2_values = [0]
    for data2 in raw_data2:
        x2_val = data2[0]['start']
        y2_val = 0
        for x2 in data2:
            y2_val += x2['rtt']/1000.0
        y2_val = y2_val/len(data2)
        x2_values.append(x2_val)
        y2_values.append(y2_val)

    plt.plot(x_values, y_values, label="No AQM")
    plt.plot(x2_values, y2_values, label="With AQM")
    plt.ylim(ymin = 0)
    plt.ylabel('RTT [ms]')
    plt.legend()
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

    x2_values = [0]
    y2_values = [0]
    for data2 in raw_data2:
        x2_val = data2[0]['start']
        y2_val = 0
        for x2 in data2:
            y2_val += x2['bytes']*8 / x2['seconds']
        y2_val = y2_val/1000
        x2_values.append(x2_val)
        y2_values.append(y2_val)

   


    plt.plot(x_values, y_values, label="No AQM")
    plt.plot(x2_values, y2_values, label="With AQM")
    plt.ylim(ymin = 0)
    plt.xlabel('time [s]')
    plt.ylabel('Throughput [kbits/s]')
    plt.legend()
    plt.suptitle('RTT & Throughput of AQM Emulator')
    fig = plt.gcf()
    fig.set_size_inches(6, 3, forward=True)
    plt.savefig('iperf3_aqm_and_noaqm.pdf', bbox_inches='tight')

res = parse_iperf3_json("iperf_noaqm.json")
res2 = parse_iperf3_json("iperf_aqm.json")
plotIperf3(res, res2)
