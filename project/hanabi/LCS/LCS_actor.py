from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
from numpy.typing import NDArray
from numpy import uint8


@dataclass
class RuleSet:
    match_string: NDArray[uint8]
    dont_care: NDArray[uint8]
    action: NDArray[uint8]
    padding: int

    @staticmethod
    def unpack_rules(rule_array: NDArray[uint8], rule_length: int):
        """
        Create RuleSet from packaged bitstring, the format for a single rule is
        [rule matching bits | don't care bits | action bits]
        each of this 3 section is padded to 8 bits
        a complete RuleSet is composed of a matrix of rules
        @param rule_array: BitMatrix
        @param rule_length: length of the actions
        @return: RuleSet
        """
        cutoff = rule_length // 8 + 1
        return RuleSet(rule_array[:, :cutoff],
                       rule_array[:, cutoff:2 * cutoff],
                       rule_array[:, 2 * cutoff:],
                       rule_length % 8)

    @staticmethod
    def empty_rules(rule_length: int, action_length: int):
        """
        Create a RuleSet with a single random rule
        @param rule_length: length of the rules
        @param action_length: length of the actions
        @return: RuleSet
        """
        return RuleSet(np.ndarray(shape=(1, rule_length // 8 + 1), dtype=uint8),
                       np.ndarray(shape=(1, rule_length // 8 + 1), dtype=uint8),
                       np.ndarray(shape=(1, action_length // 8 + 1), dtype=uint8),
                       rule_length % 8)

    @staticmethod
    def random_rule_set(rule_length: int, action_length: int, number_of_rules: int):
        """
        Create a Random Rule Set in the specified shape
        @param rule_length: int
        @param action_length: int
        @param number_of_rules: ibt
        @return: RuleSet
        """
        dont_care = ~np.packbits(np.random.randint(0, 1, (number_of_rules, rule_length)), axis=1)
        match_string = np.packbits(np.random.randint(0, 1, (number_of_rules, rule_length)), axis=1)
        action_string = np.packbits(np.random.randint(0, 1, (number_of_rules, action_length)), axis=1)
        return RuleSet(dont_care, match_string, action_string, rule_length % 8)

    def cover(self, situation: NDArray[uint8]) -> None:
        """
        Cover for an unknown event
        @param situation: sensor array
        @return: None
        """
        dont_care = ~np.packbits(np.random.randint(0, 256, (1, self.match_string.shape[1] * 8), dtype=uint8), axis=1)
        action = ~np.packbits(np.random.randint(0, 256, (1, self.action.shape[1] * 8), dtype=uint8), axis=1)
        self.match_string = np.vstack([situation, self.match_string])
        self.dont_care = np.vstack([dont_care, self.dont_care])
        self.action = np.vstack([action, self.action])

    def match(self, situation: NDArray[uint8]) -> NDArray[np.bool_]:
        """
        Match sensor array to
        @param situation: sensor array
        @return: bool array of matched rules
        """
        return np.all((self.dont_care | (~(self.match_string ^ situation))) == 255, axis=1)

    def get_action(self, index: int) -> NDArray[uint8]:
        """
        Get action from rule index
        @param index: index of the rule got from match string
        @return: action bitstring
        """
        return self.action[index]

    def pack_rules(self):
        """
        Return compressed representation of RuleSet with the following format
        [rule matching bits | don't care bits | action bits]
        each of this 3 section is padded to 8 bits
        a complete RuleSet is composed of a matrix of rules
        @return: NDarray
        """
        return np.hstack([self.match_string, self.dont_care, self.action])


class LCS_actor:
    """
    Learning Classifier System actor:
    implements the matching and covering phase
    """

    def __init__(self, sensor_list: List, rule: RuleSet, action_length: int):
        """
        Initialization method
        @param sensor_list: List of Sensors that must inherit from GenericSensor,
        they will be used to decode the environment
        @param rule: RuleSet that will be used for the actions
        @param action_length: Length of the action string
        """
        self.__sensor_list = sensor_list
        self.__sensor_size = sum(map(lambda x: x.out_size, sensor_list))
        self.__rule = rule
        self.__rule_use = []
        self.__rule_match = []
        self.__action_length = action_length

    def act(self, environment) -> NDArray[np.bool_]:
        """
        Method to get an action from the current position
        @param environment: Input of Activate Method from Sensors
        @return: np.ndarray[bool]
        """
        sensor_activation = self.__detect(environment)
        rule_activation = self.__match(sensor_activation)
        self.__rule_match.append(rule_activation)
        if np.sum(rule_activation) == 0:
            choice = self.__cover(sensor_activation)
        else:
            choice = np.random.choice(np.argwhere(rule_activation).reshape((-1,)))
        self.__rule_use.append(choice)
        action = np.unpackbits(self.__rule.get_action(choice))
        return action[:self.__action_length]

    def end_game_data(self) -> Tuple[NDArray, NDArray]:
        """
        Post-mortem data of usage of the rules,
        returns a bool matrix that represents the matched rules at each game step
        and a vector with the index of the rule that was actually used
        @return: array GameLength x NRules, array GameLength
        """
        rule_matching_data = np.vstack(self.__rule_match)
        rule_usage_data = np.array(self.__rule_use)
        return rule_matching_data, rule_usage_data

    def get_rule_set(self) -> RuleSet:
        """
        Get the ruleset
        @return: RuleSet
        """
        return self.__rule

    def __detect(self, environment) -> NDArray[uint8]:
        """
        Return Sensor output in bitstring format
        @param environment: input of Sensors
        @return: np.ndarray
        """
        actions = [sensor.activate(environment).astype(np.bool_) for sensor in self.__sensor_list]
        return np.packbits(np.hstack(actions))

    def __match(self, sensor_activation: NDArray[uint8]) -> NDArray[uint8]:
        """
        return matched rules
        @param sensor_activation: bitstring
        @return: bitstring
        """
        return self.__rule.match(sensor_activation)

    def __cover(self, sensor_activation: NDArray[uint8]) -> NDArray[uint8]:
        """
        add a new random to cover for an unmatched situation
        @param sensor_activation:
        @return:
        """
        self.__rule.cover(sensor_activation)
        self.__rule_use = np.append(self.__rule_use, 1)
        self.__rule_match = np.append(self.__rule_use, 1)
        return self.__rule_match.size - 1
