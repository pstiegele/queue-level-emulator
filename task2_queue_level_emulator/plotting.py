import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import json
import argparse

# Data for plotting
def plotQueueDelay(listQueues, drops, print_drops):
    fig, ax = plt.subplots()    
    for q in listQueues:    
        maxDepth = q['maxDepth']     
        q = q['list']   
        t=[]
        x=[]
        t_0 = q[0][0]
        for p in q:
            t.append(p[0]-t_0)
            #x.append(p[1]/1000)
            x.append(p[1]/maxDepth*100)

        ax.plot(t, x)
    
    for d in drops:
        print("Queue: " + str(d['dropQueue']) + ", Type: " + d['dropState'] + ", Time: " + str(d['time']-t_0))
        if print_drops:
            if d['dropQueue'] == 0:
                plt.axvline(x=(d['time']-t_0), ymin=0, ymax=100, linewidth=0.9, color='blue')
            else:
                plt.axvline(x=(d['time']-t_0), ymin=0, ymax=100, linewidth=0.9, color='orange')
    print("Number Drops: " + str(len(drops)))
    
    ax.set(xlabel='time (s)', ylabel='Queue Level (%)',
        title='Queue Utilization over time')
    ax.grid()

    fig.savefig("out/queueSizePlot.pdf")
    #plt.show()
    

def getDrop():
    with open('out/dropped.json', 'r') as infile:
        return json.load(infile)


def getData(q):
    with open('out/queue'+q+'.json', 'r') as infile:
        return json.load(infile)
        #return jsonObj['list']

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot queue utilization')
    parser.add_argument('--drops', dest='print_drops', action='store_true')
    parser.set_defaults(print_drops=False)
    args = parser.parse_args()
    
    print("Plot queue Utilization over time")
    q0 = getData('0')
    q1 = getData('1')
    q2 = getData('vQueue')
    drops = getDrop()
    #plotQueueDelay([q0, q1], drops)
    plotQueueDelay([q0, q1, q2], drops, args.print_drops)
