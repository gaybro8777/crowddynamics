import logging

from shapely.geometry import Point
from shapely.geometry import Polygon, GeometryCollection
from shapely.ops import cascaded_union

from crowddynamics.core.interactions import overlapping_circle_circle, \
    overlapping_three_circle
from crowddynamics.core.random.sampling import PolygonSample
from crowddynamics.multiagent import Agent
from crowddynamics.multiagent.agent import positions
from crowddynamics.multiagent.parameters import Parameters


def agent_polygon(position, radius):
    if isinstance(position, tuple):
        return cascaded_union((
            Point(position[0]).buffer(radius[0]),
            Point(position[1]).buffer(radius[1]),
            Point(position[2]).buffer(radius[2]),
        ))
    else:
        return Point(position).buffer(radius)


def overlapping(agent, position, radius):
    """
    Overlapping

    Args:
        agent (Agent):
        position:
        radius:

    Returns:
        Boolean:

    """
    if agent.three_circle:
        return overlapping_three_circle(
            agent.positions(),
            agent.radii(),
            position,
            radius,
        )
    else:
        active = agent.active
        return overlapping_circle_circle(
            agent.position[active],
            agent.radius[active],
            position,
            radius
        )


class Configuration:
    r"""
    MultiAgent simulation setup

    1) Set the Field
       - Domain
       - Obstacles
       - Targets (aka exits)

    2) Initialise Agents
       - Set maximum number of agents. This is the limit of the size of array
         inside ``Agent`` class.
       - Select Agent model.

    3) Place Agents into any surface that is contained by the domain.
       - Body type
       - Number of agents that is placed into the surface

    """

    def __init__(self, domain, agent_max_num, agent_model):
        r"""
        Simulation setup

        Args:
            domain (Polygon):
            agent_max_num (int):
            agent_model (str):
        """
        self.logger = logging.getLogger(__name__)

        # Field
        self.domain = domain
        self.obstacles = GeometryCollection()
        self.targets = GeometryCollection()
        self._occupied = Polygon()  # Currently occupied surface

        # Agents
        self.agent = Agent(agent_max_num)
        if agent_model == 'three_circle':
            self.agent.set_three_circle()
        else:
            self.agent.set_circular()

    def add_obstacle(self, obstacle):
        """
        Add new ``obstacle`` to the Field

        Args:
            obstacle (BaseGeometry):
        """
        self.obstacles |= obstacle
        self._occupied |= obstacle

    def remove_obstacle(self, obstacle):
        self.obstacles -= obstacle
        self._occupied -= obstacle

    def add_target(self, target):
        """
        Add new ``target`` to the Field

        Args:
            target (BaseGeometry):
        """
        self.targets |= target
        self._occupied |= target

    def remove_target(self, target):
        self.targets -= target
        self._occupied -= target

    def add_agents(self, num, surface, body_type='adult', iterations_limit=100):
        r"""
        Add multiple agents at once.

        1) Sample new position from ``PolygonSample``
        2) Check if agent in new position is overlapping with existing ones
        3) Add new agent if there is no overlapping

        Args:
            num (int, optional):
                - Number of agents to be placed into the ``surface``. If given
                  amount of agents does not fit into the ``surface`` only the
                  amount that fits will be placed.
                - ``None``: Places maximum size of agents

            surface (Polygon, optional):
                - ``Polygon``: Custom polygon that is contained inside the
                  domain
                - ``None``: Domain

            body_type (str):
                Choice from ``Parameter.body_types``.

            iterations_limit (int):
                Limits iterations to ``max_iter = iterations_limit * num``.

        Returns:
            int: Number of agents placed

        """
        # Draw random uniformly distributed points from the set on points
        # that belong to the surface. These are used as possible new position
        # for an agents (if it does not overlap other agents).
        ret = 0  # Number of agents places so far
        iterations = 0
        sampling = PolygonSample(surface)
        parameters = Parameters(body_type=body_type)

        while num > 0 and iterations <= iterations_limit * num:
            # Parameters
            position = sampling.draw()
            mass = parameters.mass.default()
            radius = parameters.radius.default()
            ratio_rt = parameters.radius_torso.default()
            ratio_rs = parameters.radius_shoulder.default()
            ratio_ts = parameters.radius_torso_shoulder.default()
            inertia_rot = parameters.moment_of_inertia.default()
            max_velocity = parameters.maximum_velocity.default()
            max_angular_velocity = parameters.maximum_angular_velocity.default()

            # Polygon of the agent
            if self.agent.three_circle:
                r_t = ratio_rt * radius
                r_s = ratio_rs * radius
                poly = agent_polygon(
                    positions(position, 0.0, ratio_rt * radius),
                    (r_t, r_s, r_s)
                )
            else:
                poly = agent_polygon(position, radius)

            # Conditions
            overlapping_agents = overlapping(self.agent, position, radius)
            overlapping_obstacles = self._occupied.intersects(poly)
            if not overlapping_agents and not overlapping_obstacles:
                # Add new agent
                success = self.agent.add(
                    position, mass, radius, ratio_rt, ratio_rs, ratio_ts,
                    inertia_rot, max_velocity, max_angular_velocity
                )
                if success:
                    num -= 1
                    ret += 1
                else:
                    break
            iterations += 1
        return ret
