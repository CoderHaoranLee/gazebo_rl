import numpy as np
import rospy
import gym # https://github.com/openai/gym/blob/master/gym/core.py
from gym.utils import seeding
from gazebo_connection import GazeboConnection
from openai_ros.msg import RLExperimentInfo #https://bitbucket.org/theconstructcore/theconstruct_msgs/src/master/msg/RLExperimentInfo.msg


class GymGazeboEnv(gym.Env):

  def __init__(self, start_init_physics_parameters=True, reset_world_or_sim="SIMULATION"):
    # To reset Simulations
    rospy.logdebug("START init RobotGazeboEnv")
    self.gazebo = GazeboConnection(start_init_physics_parameters,reset_world_or_sim)
    self.seed()

    # Set up ROS related variables
    self.init_position = [0, 0]
    self.goal_position = [0, 0]
    self.reward_pub = rospy.Publisher('/openai/reward', RLExperimentInfo, queue_size=1)
    rospy.logdebug("END init RobotGazeboEnv")

  # Env methods
  def seed(self, seed=None):
    self.np_random, seed = seeding.np_random(seed)
    return [seed]

  def step(self, action):
    """
    Function executed each time step.
    Here we get the action execute it in a time step and retrieve the
    observations generated by that action.
    :param action:
    :return: obs, reward, done, info
    """
    # Convert the action num to movement action
    self.gazebo.unpauseSim()
    self._take_action(action)
    self.gazebo.pauseSim()
    obs = self._get_obs()
    reward = self._compute_reward(
      obs,
      self.init_position,
      self.goal_position
    )
    done = self._is_done(obs, self.goal_position)
    info = {}

    return obs, reward, done, info

  def reset(self):
    rospy.logdebug("Reseting RobotGazeboEnvironment")
    self._reset_sim()
    self.init_position, self.goal_position = self._set_init()
    self.gazebo.unpauseSim()
    self.gazebo.pauseSim()
    obs = self._get_obs()
    rospy.logdebug("END Reseting RobotGazeboEnvironment")
    return obs

  def close(self):
    """
    Function executed when closing the environment.
    Use it for closing GUIS and other systems that need closing.
    :return:
    """
    rospy.logwarn("Closing RobotGazeboEnvironment")
    rospy.signal_shutdown("Closing RobotGazeboEnvironment")

  def _reset_sim(self):
    """Resets a simulation
    """
    rospy.logdebug("START robot gazebo _reset_sim")
    self.gazebo.pauseSim()
    self.gazebo.resetSim()
    self.gazebo.unpauseSim()
    self._check_all_systems_ready()
    self.gazebo.pauseSim()    
    rospy.logdebug("END robot gazebo _reset_sim")
    
    return True

  def _set_init(self):
    """Sets the Robot in its init pose
    """
    raise NotImplementedError()

  def _check_all_systems_ready(self):
    """
    Checks that all the sensors, publishers and other simulation systems are
    operational.
    """
    raise NotImplementedError()

  def _get_obs(self):
    """Returns the observation.
    """
    raise NotImplementedError()

  def _take_action(self, action):
    """Applies the given action to the simulation.
    """
    raise NotImplementedError()

  def _is_done(self, observations, goal_position):
    """Indicates whether or not the episode is done ( the robot has fallen for example).
    """
    raise NotImplementedError()

  def _compute_reward(self,
                      observations,
                      init_position,
                      goal_position):
    """Calculates the reward to give based on the observations given.
    """
    raise NotImplementedError()

  def _env_setup(self, initial_qpos):
    """Initial configuration of the environment. Can be used to configure initial state
    and extract information from the simulation.
    """
    raise NotImplementedError()
