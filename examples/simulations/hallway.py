from collections import namedtuple

import numpy as np

from crowd_dynamics.area import GoalRectangle
from crowd_dynamics.parameters import Parameters
from crowd_dynamics.structure.agent import Agent
from crowd_dynamics.structure.constant import Constant
from crowd_dynamics.structure.wall import LinearWall


# Path and name for saving simulation data
name = "hallway"
path = "/home/jaan/Dropbox/Projects/Crowd-Dynamics-Simulations/results"


def initialize():
    # Field
    dim = namedtuple('dim', ['width', 'height'])
    lim = namedtuple('lim', ['min', 'max'])
    d = dim(30.0, 5.0)
    x = lim(0.0, d.width)
    y = lim(0.0, d.height)

    parameters = Parameters(*d)
    constant = Constant()
    linear_params = np.array((
        ((x.min - 5, y.min), (x.max + 5, y.min)),
        ((x.min - 5, y.max), (x.max + 5, y.max)),
    ))

    linear_wall = LinearWall(linear_params)
    walls = linear_wall

    # Agents
    size = 100
    agent = Agent(*parameters.agent(size))
    first_half = slice(agent.size // 2)
    second_half = slice(agent.size // 2, None)

    parameters.random_position(agent.position[first_half], agent.radius,
                               (x.min, x.max // 2), y, walls)
    parameters.random_position(agent.position[second_half], agent.radius,
                               (x.max // 2, x.max), y, walls)

    # Goal
    direction1 = np.array((1.0, 0.0))
    direction2 = np.array((-1.0, 0.0))
    agent.target_direction[first_half] += direction1
    agent.target_direction[second_half] += direction2
    # agent.direction_to_angle()
    agent.angle[first_half] += 0
    agent.angle[second_half] += np.pi
    agent.update_shoulder_positions()

    goal = GoalRectangle(center=np.array((x.max + 2.5, y.max / 2)),
                         radius=np.array((2.5, d.height / 2)))

    goal2 = GoalRectangle(center=np.array((x.min - 2.5, y.max / 2)),
                          radius=np.array((2.5, d.height / 2)))

    goals = goal, goal2

    return constant, agent, walls, goals, path, name
