from rlutils.common.deployment import train
from rlutils.common.env_wrappers import NormaliseActionWrapper

import gym

train_parameters = {
    "project_name": "pendulum",
    "env": "Pendulum-v0",
    "model": "ddpg",
    "num_episodes": 100,
    "max_timesteps_per_episode": 500,
    # "from_pixels": False,
    "wandb_monitor": False,
    "render_freq": 0,
    "save_video": False,
    "save_final_agent": False,
}

# Make environment.
env = NormaliseActionWrapper(gym.make(train_parameters["env"]))

# Make DdpgAgent.
if train_parameters["model"] == "ddpg":
    agent_parameters = {
        "replay_capacity": 50000,
        "batch_size": 128,
        "lr_pi": 1e-4,
        "lr_Q": 1e-3,
        "gamma": 0.99,
        "tau": 1e-2,
        "noise_params": (0., 0.15, 0.5, 0.01, 300000)
    }
    from rlutils.agents.ddpg import *
    agent = DdpgAgent(env.observation_space.shape, env.action_space, agent_parameters)

run_name = train(agent, env, train_parameters)