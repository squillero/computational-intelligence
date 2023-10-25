"""
**Author:** Beatrice Occhiena s314971. See [`LICENSE`](https://github.com/beatrice-occhiena/Computational_intelligence/blob/main/LICENSE) for details.
- institutional email: `S314971@studenti.polito.it`
- personal email: `beatrice.occhiena@live.it`
- github repository: [https://github.com/beatrice-occhiena/Computational_intelligence.git](https://github.com/beatrice-occhiena/Computational_intelligence.git)

**Resources:** These notes are the result of additional research and analysis of the lecture material presented by Professor Giovanni Squillero for the Computational Intelligence course during the academic year 2023-2024 @ Politecnico di Torino. They are intended to be my attempt to make a personal contribution and to rework the topics covered in the following resources.
- [https://github.com/squillero/computational-intelligence](https://github.com/squillero/computational-intelligence)
- Stuart Russel, Peter Norvig, *Artificial Intelligence: A Modern Approach* [3th edition]
"""

from queue import SimpleQueue, LifoQueue, PriorityQueue


class Node:
    def __init__(self, state, parent=None, action_from_parent=None, path_cost=0):
        """
        Create a search Node, derived from a parent by an action.
        - tree_search Node -> ignore if already visited
        - graph_search Node -> check if already visited
        """
        self.state = state
        self.parent = parent
        self.action_from_parent = action_from_parent
        self.path_cost = path_cost
        self.depth = 0 if parent is None else parent.depth + 1
        self.is_visited = False

    def __lt__(self, other):
        """Return `True` if the path cost of the Node is less than the path cost of the other Node."""
        return self.path_cost < other.path_cost


class SearchProblem:
    def __init__(self, initial_state, goal_state=None):
        """
        Create a search problem:
        - initial_state: the initial `state` of the problem
        - goal_state: the goal `state` of the problem
        """
        self.initial_state = initial_state
        self.goal_state = goal_state

    def actions(self, state):
        """Return the `list` of actions that can be executed in the given state."""
        raise NotImplementedError

    def apply_action(self, state, action):
        """Return the `state` that results from executing the given action in the given state."""
        raise NotImplementedError

    def action_cost(self, state1, action, state2):
        """
        Return the cost of executing the given action in the given state.
        - The default method returns 1.
        """
        return 1

    def expand(self, node):
        """Return the `list` of successors Nodes of the given Node."""
        successors = []
        for action in self.actions(node.state):
            new_state = self.apply_action(node.state, action)
            new_node = Node(new_state, node, action, node.path_cost + self.action_cost(node.state, action, new_state))
            successors.append(new_node)
        return successors

    def is_goal(self, state):
        """Return `True` if the given state is a goal state, `False` otherwise."""
        return state == self.goal

    def h(self, node):
        """
        Return an heuristic estimation of the cost to reach the goal from the given state.
        - The default method returns 0.
        """
        return 0

    def retrieve_path(self, node):
        """Return the `list` of actions that leads to the given Node."""
        path = []
        while node.parent is not None:
            path.append(node.action_from_parent)
            node = node.parent
        return path[::-1]


class SearchStrategy:
    def __init__(self, search_type, strategy_name, limit=None):
        """
        1. Select a search type by name.
        - `tree_search`
        - `graph_search`

        2. Select a search strategy by name.

        UNINFORMED:
        - `breadth_first`
        - `depth_first`
        - `uniform_cost`
        - `depth_limited`
        - `iterative_deepening`
        - `bidirectional`

        INFORMED:
        - `greedy_best_first`
        - `a_star`

        3. Optionally select a limit, the maximum depth of the search tree (used only by depth_limited search strategy).
        ---
        `steps` and `max_frontier_size` are variables used to evaluate the performance of the search strategy.
        """
        self.search_type = search_type
        self.strategy_name = strategy_name
        self.limit = limit
        self.steps = 0
        self.max_frontier_size = 0

    def reset(self):
        """Reset the variables used to evaluate the performance of the search strategy."""
        self.steps = 0
        self.max_frontier_size = 0

    def print_solution(self, problem, solution):
        """
        Print the solution of the given problem.
        - solution: the solution Node of the problem
        """
        print('Search type:', self.search_type)
        print('Strategy:', self.strategy_name)
        if self.limit is not None and self.strategy_name == 'depth_limited':
            print('Limit:', self.limit)
        print('----------------------')

        if solution is None:
            print('No solution found.')
        else:
            print('Solution found:')
            print('Path:', problem.retrieve_path(solution))
            print('Path cost:', solution.path_cost)
            print('Number of steps:', self.steps)
            print('Max frontier size:', self.max_frontier_size)

    def search(self, problem):
        """
        Return the solution Node of the given problem using the selected search strategy or None if no solution is found.
        """
        self.reset()

        if self.strategy_name == 'breadth_first':
            return SearchStrategy.breadth_first_search(self, problem, self.search_type)
        elif self.strategy_name == 'depth_first':
            return SearchStrategy.depth_first_search(self, problem, self.search_type)
        elif self.strategy_name == 'uniform_cost':
            return SearchStrategy.uniform_cost_search(self, problem, self.search_type)
        elif self.strategy_name == 'depth_limited':
            if self.limit is None:
                raise ValueError('No limit given.')
            return SearchStrategy.depth_limited_search(self, problem, self.limit, self.search_type)
        elif self.strategy_name == 'iterative_deepening':
            return SearchStrategy.iterative_deepening_search(self, problem, self.search_type)
        elif self.strategy_name == 'bidirectional':
            return SearchStrategy.bidirectional_search(self, problem)
        elif self.strategy_name == 'greedy_best_first':
            return SearchStrategy.greedy_best_first_search(self, problem, self.search_type)
        elif self.strategy_name == 'a_star':
            return SearchStrategy.a_star_search(self, problem, self.search_type)
        else:
            raise ValueError('Invalid search strategy name.')

    def breadth_first_search(self, problem, search_type='tree_search'):
        """
        Return the solution Node of the given problem using the breadth-first search algorithm or None if no solution is found.
        - search_type: select 'tree_search' or 'graph_search'
        - frontier: implemented by a `FIFO queue`
        """
        frontier = SimpleQueue()
        frontier.put(Node(problem.initial_state))
        while not frontier.empty():
            node = frontier.get()
            if problem.is_goal(node.state):
                return node
            self.steps += 1
            self.max_frontier_size = max(self.max_frontier_size, frontier.qsize())
            for child in problem.expand(node):
                if search_type == 'tree_search' or not child.is_visited:
                    frontier.put(child)
                    self.max_frontier_size = max(self.max_frontier_size, frontier.qsize())
                    child.is_visited = True
        return None

    def depth_first_search(self, problem, search_type='tree_search'):
        """
        Return the solution Node of the given problem using the depth-first search algorithm or None if no solution is found.
        - search_type: select 'tree_search' or 'graph_search'
        - frontier: implemented by a `LIFO queue`
        """
        frontier = LifoQueue()
        frontier.put(Node(problem.initial_state))
        while not frontier.empty():
            node = frontier.get()
            if problem.is_goal(node.state):
                return node
            self.steps += 1
            self.max_frontier_size = max(self.max_frontier_size, frontier.qsize())
            for child in problem.expand(node):
                if search_type == 'tree_search' or not child.is_visited:
                    frontier.put(child)
                    child.is_visited = True
        return None

    def uniform_cost_search(self, problem, search_type='tree_search'):
        """
        Return the solution Node of the given problem using the uniform-cost search algorithm or None if no solution is found.
        - search_type: select 'tree_search' or 'graph_search'
        - frontier: implemented by a `Priority queue` with path cost as priority
        """
        frontier = PriorityQueue()
        frontier.put((0, Node(problem.initial_state)))
        while not frontier.empty():
            node = frontier.get()[1]
            if problem.is_goal(node.state):
                return node
            self.steps += 1
            self.max_frontier_size = max(self.max_frontier_size, frontier.qsize())
            for child in problem.expand(node):
                if search_type == 'tree_search' or not child.is_visited:
                    frontier.put((child.path_cost, child))
                    child.is_visited = True
        return None

    def depth_limited_search(self, problem, limit, search_type='tree_search'):
        """
        Return the solution Node of the given problem using the depth-limited search algorithm or None if no solution is found within the given limit.
        - limit: the maximum depth of the search tree
        - search_type: select 'tree_search' or 'graph_search'
        - frontier: implemented by a `LIFO queue`
        """
        frontier = LifoQueue()
        frontier.put(Node(problem.initial_state))
        while not frontier.empty():
            node = frontier.get()
            if problem.is_goal(node.state):
                return node
            if node.depth < limit:
                self.steps += 1
                self.max_frontier_size = max(self.max_frontier_size, frontier.qsize())
                for child in problem.expand(node):
                    if search_type == 'tree_search' or not child.is_visited:
                        frontier.put(child)
                        child.is_visited = True
        return None

    def iterative_deepening_search(self, problem, search_type='tree_search'):
        """
        Return the solution Node of the given problem using the iterative deepening search algorithm or None if no solution is found.
        - search_type: select 'tree_search' or 'graph_search'
        - frontier: implemented by a `LIFO queue`
        """
        limit = 0
        while True:
            result = SearchStrategy.depth_limited_search(self, problem, limit, search_type)
            if result is not None:
                return result
            limit += 1

    def bidirectional_search(self, problem):
        """
        Return the solution Node of the given problem using the bidirectional search algorithm or None if no solution is found.
        - frontiers: implemented by a `FIFO queue`
        """
        frontier_start = SimpleQueue()
        frontier_start.put(Node(problem.initial_state))

        frontier_goal = SimpleQueue()
        frontier_goal.put(Node(problem.goal_state))

        while not frontier_start.empty() and not frontier_goal.empty():
            node_start = frontier_start.get()
            node_goal = frontier_goal.get()
            if node_start.state == node_goal.state:
                return node_start, node_goal
            self.steps += 2
            self.max_frontier_size = max(self.max_frontier_size, frontier_start.qsize() + frontier_goal.qsize())
            for child_start in problem.expand(node_start):
                frontier_start.put(child_start)
            for child_goal in problem.expand(node_goal):
                frontier_goal.put(child_goal)
        return None

    def greedy_best_first_search(self, problem, search_type='tree_search'):
        """
        Return the solution Node of the given problem using the greedy best-first search algorithm or None if no solution is found.
        - search_type: select 'tree_search' or 'graph_search'
        - frontier: implemented by a `Priority queue` with heuristic as priority
        """
        frontier = PriorityQueue()
        frontier.put((problem.h(Node(problem.initial_state)), Node(problem.initial_state)))
        while not frontier.empty():
            node = frontier.get()[1]
            if problem.is_goal(node.state):
                return node
            self.steps += 1
            self.max_frontier_size = max(self.max_frontier_size, frontier.qsize())
            for child in problem.expand(node):
                if search_type == 'tree_search' or not child.is_visited:
                    frontier.put((problem.h(child), child))
                    child.is_visited = True
        return None

    def a_star_search(self, problem, search_type='tree_search'):
        """
        Return the solution Node of the given problem using the A* search algorithm or None if no solution is found.
        - search_type: select 'tree_search' or 'graph_search'
        - frontier: implemented by a `Priority queue` with heuristic + path cost as priority
        """
        frontier = PriorityQueue()
        frontier.put((problem.h(Node(problem.initial_state)) + 0, Node(problem.initial_state)))
        while not frontier.empty():
            node = frontier.get()[1]
            if problem.is_goal(node.state):
                return node
            self.steps += 1
            self.max_frontier_size = max(self.max_frontier_size, frontier.qsize())
            for child in problem.expand(node):
                if search_type == 'tree_search' or not child.is_visited:
                    frontier.put((problem.h(child) + child.path_cost, child))
                    child.is_visited = True
        return None
