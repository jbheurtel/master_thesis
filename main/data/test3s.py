import math

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from mpl_toolkits.mplot3d import Axes3D


def get_time(n, l):
    return math.pow(n, 1.5) * math.pow(l, 0.5)/ 1000 + 0.5

n_requests = np.arange(0, 51, 1)
limits = np.arange(0, 50001, 1000)

import pandas as pd
df = pd.DataFrame(index=limits, columns=n_requests)
for n in n_requests:
    for l in limits:
        df.loc[l, n] = get_time(n, l)



## Matplotlib Sample Code using 2D arrays via meshgrid
X = np.arange(-5, 5, 0.25)
Y = np.arange(-5, 5, 0.25)


X, Y = np.meshgrid(n_requests, limits)
Z = df.values

fig = plt.figure()
ax = Axes3D(fig)
surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)

ax.zaxis.set_major_locator(LinearLocator(10))
ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

fig.colorbar(surf, shrink=0.5, aspect=5)
plt.title('Original Code')
plt.show()