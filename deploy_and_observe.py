from rlutils.common.deployment import deploy
from rlutils.common.env_wrappers import NormalizedEnv
from rlutils.common.observer import Observer

import gym
from joblib import load

# RUN_NAME = "cosmic-yogurt-123"
RUN_NAME = "jumping-sun-13"

deploy_parameters = {
    "num_episodes": 1000,
    "max_timesteps_per_episode": 500,
    "wandb_monitor": False,
    "render_freq": 1,
    "save_final_agent": False
}

# Create observer class.
observer = Observer(
                    # state_dim_names=["pos", "vel", "ang", "vel_ang"],
                    state_dim_names=["pos_x","pos_y","vel_x","vel_y","ang","vel_ang","left_contact","right_contact"],
                    # action_dim_names=["action_idx"]
                    action_dim_names=["main_engine","lr_engine"]
                    )

# Deploy agent in environment.
deploy(agent=load(f"saved_runs/{RUN_NAME}.joblib"),
    #    env=gym.make("CartPole-v1"),
       env=NormalizedEnv(gym.make("LunarLanderContinuous-v2")),
       parameters=deploy_parameters,
       observer=observer
       )

observer.dataframe().to_csv(f"{RUN_NAME}.csv")