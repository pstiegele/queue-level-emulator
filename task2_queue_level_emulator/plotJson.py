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

def readFiletoString(file_name):
    file = open(file_name, "r")
    content = file.read()
    return content

def parse_iperf3_json(path):
    content = readFiletoString(path)
    content = json.loads(content)
    #now content is a dict
    loRawInputs = content['intervals']
    resLst = []
    for x in loRawInputs:
        innerLst = []
        for y in x['streams']:
            innerLst.append(y) #TODO hier wird nur der erste Stream geparst
        resLst.append(innerLst)
    return  resLst

def plotIperf3(raw_data, out):

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
        #    y_val += x['bytes'] / x['seconds']
	        y_val += x['bits_per_second']
        y_val = y_val/1000
        x_values.append(x_val)
        y_values.append(y_val)

    plt.plot(x_values, y_values)
    plt.ylim(ymin = 0)
    plt.xlabel('time [s]')
    plt.ylabel('Throughput [kbit/s]')
    plt.suptitle('iperf3 json output')
    fig = plt.gcf()
    fig.set_size_inches(6, 3, forward=True)
    plt.savefig(out, bbox_inches='tight')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create matplot graph of json')
    parser.add_argument('--path', type=str , default="out/iperf_client_1.json", action='store',  help='path to json')
    parser.add_argument('--out', type=str , default="out/server1.pdf", action='store',  help='path to output pdf')
    args = parser.parse_args()
    #print(args.path)
    parsed = parse_iperf3_json(args.path)
    plotIperf3(parsed, args.out)
