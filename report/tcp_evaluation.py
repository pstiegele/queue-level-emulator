import numpy as np
import matplotlib.pyplot as plt


labels = ['ip_forward', 'Python 3', 'Python 2', 'C', 'Go', 'Rust']
tcp_means = [5830, 1289, 1394, 1793, 3445, 712]
#tcp_std = [0.014, 0.040, 0.099, 22.737, 0.396, 0.035]
width = 0.35       # the width of the bars: can also be len(x) sequence

fig, ax = plt.subplots()

#ax.bar(labels, tcp_means, width, yerr=tcp_std, label='TCP bandwidth')
ax.bar(labels, tcp_means, width, label='TCP bandwidth')
#ax.set_yscale('log')
ax.set_ylabel('Mbits/sec')
ax.set_title('TCP bandwidth per language')
ax.legend()

plt.show()
