import matplotlib
matplotlib.use('TkAgg') # do this before importing pylab
import matplotlib.pyplot as plt
import random

fig = plt.figure()
ax = fig.add_subplot(111)

x = range(30)
y = [random.random() for i in x]
line, = ax.plot(x,y)

def animate(*args):
    n = len(y)
    while True:
        data = random.random()
        y.append(data)

        n += 1
        line.set_data(range(n-30, n), y[-30:])
        ax.set_xlim(n-31, n-1)
        fig.canvas.draw()

fig.canvas.manager.window.after(100, animate)
plt.show()