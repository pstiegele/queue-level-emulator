import numpy as np
import matplotlib.pyplot as plt


labels = ['ip_forward', 'Python 3', 'Python 2', 'C', 'Go', 'Rust']
ping_means = [0.023, 0.107, 0.092, 13.543, 0.112, 0.120]
#ping_std = [0.014, 0.040, 0.099, 22.737, 0.396, 0.035]
width = 0.35       # the width of the bars: can also be len(x) sequence

fig, ax = plt.subplots()

ax.bar(labels, ping_means, width, label='Ping RTT')
ax.set_yscale('log')
ax.set_ylabel('ms')
ax.set_title('Ping RTT duration per language')
ax.legend()

plt.show()
