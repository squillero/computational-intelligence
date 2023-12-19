# Snake with  RL

The code in the folder aims to train a Network through Reinforcement Learning with the Deep Q Learning method.

It uses as a state a concatenation of the 8 neighboring cells of the snake head, the one hot encoding of the direction (4 inputs) and 2 inputs for the position of the apple, two hidden layers of 256 and 128 neurons and finally 4 output states for the actions. The 4 output will be an estimation of the maximum reward obtainable if we choose that action.

It uses Epsilon-Greedy Exploration Strategy (with linear decrease) to train the network on "wrong" actions.

To stabilize the training two twin network are used, one, the main will be fitted on the temporal difference calculated on the second, the target, with the following formula: 
$$R_t + \gamma \max_a Q(s_{t+1},a)$$

The snake is rewarded more when it eats an apple, and is penalized when it hits a wall or itself or if it survives too long with the same length (it basically starves) to avoid it circling around infinitely.

_by Vincenzo Micciche'_


