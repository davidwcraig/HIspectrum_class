"""
A test program to learn about mouse events in matplotlib
D. Craig 2023-07-17
based in docs at: https://matplotlib.org/stable/users/explain/event_handling.html
"""

import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(np.random.rand(10))  # random data
event_list = [] # a list to hold mouse event data

def onclick(event):
    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata))
    event_list.append([event.button, event.xdata, event.ydata])

cid = fig.canvas.mpl_connect('button_press_event', onclick)
plt.show() # think this blocks until the canvas is dropped via mouse, etc.

fig.canvas.mpl_disconnect(cid)

