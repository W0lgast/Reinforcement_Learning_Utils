import torch.nn as nn
import torch.optim as optim


class SequentialNetwork(nn.Module):
    def __init__(self, layers=None, code=None, preset=None, input_shape=None, output_size=None,
                 eval_only=False, optimiser=optim.Adam, lr=1e-3, clip_grads=False):
        super(SequentialNetwork, self).__init__() 
        if layers is None: 
            if code is not None:
                layers = code_parser(code)
            else:
                assert preset is not None, "Must specify layers, code or preset."
                assert input_shape is not None and output_size is not None, "Must specify input_shape and output_size."
                layers = sequential_presets(preset, input_shape, output_size)
        self.layers = nn.Sequential(*layers)
        if eval_only: self.eval()
        else: 
            self.optimiser = optimiser(self.parameters(), lr=lr)
            self.clip_grads = clip_grads

    def forward(self, x): return self.layers(x)

    def optimise(self, loss, retain_graph=True): 
        self.optimiser.zero_grad()
        loss.backward(retain_graph=retain_graph) 
        if self.clip_grads: # Optional gradient clipping.
            for param in self.parameters(): param.grad.data.clamp_(-1, 1) 
        self.optimiser.step()

# class MultiHeadedNetwork(nn.Module):
#     def __init__(self, common=None, heads=None, preset=None, input_shape=None, output_size=None):
#         super(MultiHeadedNetwork, self).__init__() 
#         if common is None: 
#             assert preset is not None, "Must specify either layers or preset."
#             assert input_shape is not None and output_size is not None, "Must specify input_shape and output_size."
#             common, heads = multi_headed_presets(preset, input_shape, output_size)
#         self.common = nn.Sequential(*common)
#         self.heads = nn.ModuleList([nn.Sequential(*head) for head in heads])

#     def forward(self, x): 
#         x = self.common(x)
#         return tuple(head(x) for head in self.heads)


def code_parser(code):
    layers = []
    for l in code:
        if type(l[0]) == int:   layers.append(nn.Linear(l[0], l[1]))
        elif l == "R":          layers.append(nn.ReLU())
        elif l == "T":          layers.append(nn.Tanh())
        elif l == "S":          layers.append(nn.Softmax(dim=1))
        elif l[0] == "D":       layers.append(nn.Dropout(p=0.6))
        elif l[0] == "B":       layers.append(nn.BatchNorm2d(l[1]))
    return layers


# ===================================================================
# PRESETS


def sequential_presets(name, input_shape, output_size):

    if name == "CartPolePi_Pixels":
        # Just added Softmax to Q version.
        def conv2d_size_out(size, kernel_size=5, stride=2):
            return (size - (kernel_size - 1) - 1) // stride  + 1
        convw = conv2d_size_out(conv2d_size_out(conv2d_size_out(input_shape[3])))
        convh = conv2d_size_out(conv2d_size_out(conv2d_size_out(input_shape[2])))
        linear_input_size = convw * convh * 32
        return [
            nn.Conv2d(input_shape[1], 16, kernel_size=5, stride=2),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.Conv2d(16, 32, kernel_size=5, stride=2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(32, 32, kernel_size=5, stride=2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(linear_input_size, output_size),
            nn.Softmax(dim=1)
        ]

    # if name == "CartPolePi_Vector":
    #     return [
    #         nn.Linear(input_shape[0], 64), 
    #         nn.ReLU(),
    #         nn.Linear(64, 128), 
    #         # nn.Dropout(p=0.6),
    #         nn.ReLU(),
    #         nn.Linear(128, output_size),
    #         nn.Softmax(dim=1)
    #     ]

    if name == "CartPoleQ_Pixels":
        # From https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html.
        def conv2d_size_out(size, kernel_size=5, stride=2):
            return (size - (kernel_size - 1) - 1) // stride  + 1
        convw = conv2d_size_out(conv2d_size_out(conv2d_size_out(input_shape[3])))
        convh = conv2d_size_out(conv2d_size_out(conv2d_size_out(input_shape[2])))
        linear_input_size = convw * convh * 32
        return [
            nn.Conv2d(input_shape[1], 16, kernel_size=5, stride=2),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.Conv2d(16, 32, kernel_size=5, stride=2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(32, 32, kernel_size=5, stride=2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(linear_input_size, output_size)
        ]

    # if name == "CartPoleQ_Vector":
    #     # From https://github.com/transedward/pytorch-dqn/blob/master/dqn_model.py.
    #     return [
    #         nn.Linear(input_shape[0], 256),
    #         nn.ReLU(),
    #         nn.Linear(256, 128),
    #         nn.ReLU(),
    #         nn.Linear(128, 64),
    #         nn.ReLU(),
    #         nn.Linear(64, output_size)
    #     ]

    if name == "CartPoleV_Pixels":
        # Just change Q version to have one output node.
        def conv2d_size_out(size, kernel_size=5, stride=2):
            return (size - (kernel_size - 1) - 1) // stride  + 1
        convw = conv2d_size_out(conv2d_size_out(conv2d_size_out(input_shape[3])))
        convh = conv2d_size_out(conv2d_size_out(conv2d_size_out(input_shape[2])))
        linear_input_size = convw * convh * 32
        return [
            nn.Conv2d(input_shape[1], 16, kernel_size=5, stride=2),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.Conv2d(16, 32, kernel_size=5, stride=2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(32, 32, kernel_size=5, stride=2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(linear_input_size, 1)
        ]

    # if name == "CartPoleV_Vector":
    #     return [
    #         nn.Linear(input_shape[0], 64), 
    #         nn.ReLU(),
    #         nn.Linear(64, 128), 
    #         # nn.Dropout(p=0.6),
    #         nn.ReLU(),
    #         nn.Linear(128, 1)
    #     ]

    # if name == "PendulumPi_Vector":
    #     # From https://towardsdatascience.com/deep-deterministic-policy-gradients-explained-2d94655a9b7b.
    #     return [
    #         nn.Linear(input_shape[0], 256),
    #         nn.ReLU(),
    #         nn.Linear(256, 256),
    #         nn.ReLU(),
    #         nn.Linear(256, output_size),
    #         nn.Tanh()
    #     ]

    # if name == "PendulumQ_Vector":
    #     return [
    #         nn.Linear(input_shape[0], 256),
    #         nn.ReLU(),
    #         nn.Linear(256, 256),
    #         nn.ReLU(),
    #         nn.Linear(256, output_size)
    #     ]

    # if name == "StableBaselinesPi_Vector":
    #     # From https://towardsdatascience.com/deep-deterministic-policy-gradients-explained-2d94655a9b7b.
    #     return [
    #         nn.Linear(input_shape[0], 64),
    #         nn.ReLU(),
    #         nn.Linear(64, 64),
    #         nn.ReLU(),
    #         nn.Linear(64, output_size),
    #         nn.Tanh()
    #     ]

    # if name == "StableBaselinesQ_Vector":
    #     return [
    #         nn.Linear(input_shape[0], 64),
    #         nn.ReLU(),
    #         nn.Linear(64, 64),
    #         nn.ReLU(),
    #         nn.Linear(64, output_size)
    #     ]

    raise NotImplementedError(f"Invalid preset name {name}.")


# def multi_headed_presets(name, input_shape, output_size):

#     if name == "CartPolePiAndV_Vector":
#         # From https://github.com/pytorch/examples/blob/master/reinforcement_learning/reinforce.py. 
#         # and https://github.com/pytorch/examples/blob/master/reinforcement_learning/actor_critic.py.
#         # (The latter erroneously describes the model as actor-critic; it's REINFORCE with baseline!)
#         return ([ # Common.
#             nn.Linear(input_shape[0], 128), 
#             nn.Dropout(p=0.6),
#             nn.ReLU()
#         ], 
#         [
#             [ # Policy head.
#                 nn.Linear(128, output_size),
#                 nn.Softmax(dim=1)
#             ],
#             [ # Value head.
#                 nn.Linear(128, 1)
#             ]
#         ])

#     raise NotImplementedError(f"Invalid preset name {name}.")