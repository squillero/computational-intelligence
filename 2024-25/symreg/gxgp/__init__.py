#   *        Giovanni Squillero's GP Toolbox
#  / \       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2   +      A no-nonsense GP in pure Python
#    / \
#  10   11   Distributed under MIT License

try:
    from icecream import install

    install()
except ImportError:
    pass

from .draw import *
from .gp_common import *
from .gp_dag import *
from .gp_tree import *
from .node import *
from .random import gxgp_random
from .utils import *
