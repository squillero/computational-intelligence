import unittest
import numpy as np
from numpy import bool_
from numpy.typing import NDArray

from project.hanabi.LCS import RuleSet
from project.hanabi.LCS import LCS_actor
from project.hanabi.LCS import GenericSensor


def get_default_rule_set():
    rule = np.array([[1, 0, 0, 1],
                     [0, 1, 0, 1]])
    dont = np.array([[0, 0, 1, 0],
                     [0, 0, 1, 0]])
    action = np.array([[1, 0], [0, 1]])
    ruleset = np.hstack([np.packbits(rule, axis=1), np.packbits(dont, axis=1), np.packbits(action, axis=1)])
    return RuleSet.unpack_rules(ruleset, 4)


class rightSensor(GenericSensor):

    def activate(self, knowledge_map) -> NDArray[bool_]:
        return np.ones(1)


class wrongSensor(GenericSensor):

    def activate(self, knowledge_map) -> NDArray[bool_]:
        return np.zeros(1)


class RuleSetTest(unittest.TestCase):
    def test_match(self):
        environment1 = np.packbits(np.array([1, 0, 0, 1]))
        environment2 = np.packbits(np.array([0, 0, 0, 0]))
        environment3 = np.packbits(np.array([0, 1, 1, 1]))
        rules = get_default_rule_set()
        self.assertEqual(list(rules.match(environment1)), [True, False])
        self.assertEqual(list(rules.match(environment2)), [False, False])
        self.assertEqual(list(rules.match(environment3)), [False, True])

    def test_cover(self):
        ruleset = RuleSet.empty_rules(4, 2)
        environment1 = np.packbits(np.array([1, 0, 0, 1]))
        ruleset.cover(environment1)
        self.assertEqual(list(ruleset.match(environment1))[0], [True])
        ruleset.cover(environment1)
        self.assertEqual(list(ruleset.match(environment1))[:2], [True, True])
        ruleset.cover(environment1)
        self.assertEqual(list(ruleset.match(environment1))[:3], [True, True, True])

    def test_random(self):
        params = {
            'rule_length': 100,
            'action_length': 4,
            'number_of_rules': 10
        }
        ruleset = RuleSet.random_rule_set(**params)
        q1 = (params['number_of_rules'], params['rule_length'] // 8 + 1)
        q2 = (params['number_of_rules'], params['action_length'] // 8 + 1)
        self.assertEqual(ruleset.match_string.shape, q1)
        self.assertEqual(ruleset.dont_care.shape, q1)
        self.assertEqual(ruleset.action.shape, q2)


class LCSTest(unittest.TestCase):
    def test_action(self):
        rule_set = get_default_rule_set()
        sensor_list = [wrongSensor(1), rightSensor(1), wrongSensor(1), rightSensor(1)]  # 0101
        lcs = LCS_actor(sensor_list=sensor_list, rule=rule_set, action_length=2)
        self.assertEqual(list(lcs.act(None)), [0, 1])
        self.assertEqual(list(lcs.act(None)), [0, 1])

    def test_end_game_data(self):
        rule_set = get_default_rule_set()
        sensor_list = [wrongSensor(1), rightSensor(1), wrongSensor(1), rightSensor(1)]  # 0101
        lcs = LCS_actor(sensor_list=sensor_list, rule=rule_set, action_length=2)
        [lcs.act(None) for _ in range(10)]
        matching_data, usage_data = lcs.end_game_data()
        self.assertEqual(matching_data.shape, (10, 2))
        self.assertEqual(usage_data.shape, (10,))
        expected_match = np.zeros((10, 2))
        expected_match[:, 1] = 1
        self.assertTrue(np.all(matching_data == expected_match))
        self.assertEqual(list(usage_data), [1]*10)


if __name__ == '__main__':
    unittest.main()
