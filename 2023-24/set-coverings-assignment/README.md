# Set Covering

Proposal of solution of the Set Cover assignment


Problem representation:
if a set covers a certain position of the given space the value will be set to True. False otherwhise.


The proposal uses the A* search to minimize the number of the set required to completly cover a given space. My proposal considers two different euristics for the A* star algorithm.
The fist euristics is more "naive" and tries to minimize th overlapping and to maximize the extension (new number of true element in the new_state).
The second euristic is a bit more sophisticated and tries to estimate how many set i will need to fully cover the given set if a choose a set from the list of possible sets.


Some preprocessing is also done to consider some (rare) edge cases.
Credits to [PaolaMts](https://github.com/PaolaMts) for the forced_sets function