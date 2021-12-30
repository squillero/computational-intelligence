from abc import ABC, abstractmethod
from numpy.typing import NDArray
from numpy import bool_


class GenericSensor(ABC):
    """
    Abstract Class that must be inherited for creating a new sensor
    """
    out_size = 1

    def __init__(self, out_size: int):
        """
        Constructor for Generic Sensor
        @param out_size: length of the outputted bit_string
        """
        out_size = out_size

    @abstractmethod
    def activate(self, knowledge_map) -> NDArray[bool_]:
        """
        Activate method that must be overloaded
        @param knowledge_map: Environment descriptor
        @return: bool array of 'self.out_size' length
        """
        pass
