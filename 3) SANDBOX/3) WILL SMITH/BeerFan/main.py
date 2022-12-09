import matplotlib as mpl
import matplotlib.pylab as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import numpy as np

time_step = 0.2  # seconds


class Fan:
    def __init__(self, string_offset=18, start_position=0, start_velocity=0, acceleration=1, max_velocity=100):
        self.string_offset = string_offset
        self.position = start_position
        self.velocity = start_velocity
        self.acceleration = acceleration
        self.max_velocity = max_velocity

    def update_position(self, t_step):
        if self.velocity < self.max_velocity:
            self.velocity = self.velocity + t_step * self.acceleration
        elif self.velocity >= self.max_velocity:
            self.velocity = self.max_velocity
        self.position = (self.position + t_step * self.velocity)%(np.pi*2)

    def get_stringXY(self):
        x = np.cos(self.position)*self.string_offset
        y = np.sin(self.position)*self.string_offset
        return [x, y]

    def DEBUG_plot_fan(self):

def plot_frame(x, y, z):
    mpl.rcParams['legend.fontsize'] = 10

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.plot(x, y, z, label='parametric curve')
    ax.legend()

    plt.show()


if __name__ == '__main__':
    a = np.linspace(0, 4 * np.pi, 200)

    X = np.cos(a)
    Y = np.sin(a)
    Z = np.linspace(0, 2, 200)

    plot_frame(X, Y, Z)
