import numpy as np
from collections import OrderedDict
from numba import jitclass, float64

from source.field.agent import agent_struct, initial_position, initial_velocity
from source.field.wall import LinearWall


spec_constant = OrderedDict(
    tau_adj=float64,
    k=float64,
    tau_0=float64,
    sight=float64,
    f_max=float64,
    mu=float64,
    kappa=float64,
    a=float64,
    b=float64,
)


@jitclass(spec_constant)
class Constant(object):
    def __init__(self):
        self.sight = 7.0
        self.f_max = 1e3
        self.tau_adj = 0.5
        self.k = 1.5 * 70
        self.tau_0 = 3.0
        self.mu = 1.2e5
        self.kappa = 2.4e5
        self.a = 2e3
        self.b = 0.08


constant = Constant()

x_dims = (0, 10)
y_dims = (0, 10)

linear_params = np.array((((0, 0), (0, 10)),
                          ((0, 0), (10, 0)),
                          ((0, 10), (10, 10))), dtype=np.float64
                         )

linear_wall = LinearWall(linear_params)

amount = 100
mass = np.random.uniform(60.0, 80.0, amount)
radius = np.random.uniform(0.2, 0.3, amount)
goal_velocity = 2.5

position = initial_position(amount, x_dims, y_dims, radius, linear_wall)
velocity = initial_velocity(amount)
goal_direction = velocity

agent = agent_struct(mass, radius, position, velocity, goal_velocity,
                     goal_direction)