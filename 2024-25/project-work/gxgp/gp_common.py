#   *        Giovanni Squillero's GP Toolbox
#  / \       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2   +      A no-nonsense GP in pure Python
#    / \
#  10   11   Distributed under MIT License

from copy import deepcopy

from .node import Node
from .random import gxgp_random


def xover_swap_subtree(tree1: Node, tree2: Node) -> Node:
    offspring = deepcopy(tree1)
    ic(offspring)
    successors = None
    while not successors:
        node = gxgp_random.choice(list(offspring.subtree))
        successors = node.successors
    i = gxgp_random.randrange(len(successors))
    ic(successors, i)
    successors[i] = deepcopy(gxgp_random.choice(list(tree2.subtree)))
    ic(successors, i)
    node.successors = successors
    return offspring
