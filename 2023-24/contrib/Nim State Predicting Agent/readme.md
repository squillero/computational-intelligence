# Evolutionary Logistic Classifier - best results
#### Strategy description

The nim game is a so called 'impartial game'. This means that every state of the game can be labbeled as a P-state (P-position) or a N-state (N-position). In particular, the P-state means that the state is advantageous for the previous player (the one that just moved), while the N-state means that the state is advantageous for the next player.

The strategy is to get a logistic classifier that can predict if the next state (after my agent makes the moves) is a P-state or a N-state, in order to always move into a P-state. The way we choose the next move is by simulating all possible moves and evaluating every possible next state, choosing finally the one we are more confident its advantageous to us. 

The inputs of the logistic classifier are some hand-made extracted features that give information about the state of the game, eg. number of non-zero rows, maximum row, meadian value of non-zero rows, ecc.. Furthermore, the initial features are then enriched with their polynomial combinations, up to the third degree, thus having to optimise up to 165 weights.

Since the problem of training a logistic classifier is a 'supervised learning' one, meaning we have to give the model inputs and answers for him to train, and we don't have a dataset (furthermore we cannot create it, as we pretend not to have the optimal agent), the way the agent was optimised was by searching for its weights through an evolutionary strategy taking as a fitness the estimated average win-rate against another agent.

#### Implementation details
The __genome__ is, as described before, the weight given to each feature extracted from the state (as well as their polynomial combinations).

The __mutations__ are done by adding a random number sampled from a gaussian to a random parameter. The standard deviation of the gaussian gets smaller as we get closer to the final generation, in order to produce finer deviations from the best solutions as we get to the end.

The __fitness__ used during training is simply the average win-rate against the ```optimal``` strategy over 100 games. The fitness used in the results, instead, takes the best agent in the last generation (selected with the 100 games) and plays 1000 games (to decrease uncertainty) against all available agents.

The __simulation length__ was of 150 generations, each having 1 parent (best agent of the previous generation) and 20 new individuals. The simulation was sped up by threading the evaluation step.

#### Results
```
Fitness (vs. random) -> 0.926
Fitness (vs. gabriele) -> 1.0
Fitness (vs. optimal) -> 0.969
Fitness (vs. expert_system) -> 0.0
```
