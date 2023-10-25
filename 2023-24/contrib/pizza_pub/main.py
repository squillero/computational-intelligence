from queue import Queue
from state import State

FRIENDS_COUNT = 6


def explore_tree(queue: Queue[State], iteraton_limit=None) -> list[State] | None:
    discovered_sates: set[State] = set()
    while iteraton_limit if iteraton_limit else True:
        iteraton_limit -= 1
        current_state: State = queue.get()
        adjacents: set[State] = current_state.generate_adjacents()
        for adj in adjacents:
            if adj in discovered_sates:
                continue
            if adj.is_solution():
                print(f'Solution found after analyzing {len(discovered_sates)} states')
                return adj.ancestor_states()
            queue.put(adj)
        discovered_sates.add(current_state)
    return None


def main():
    initial_state = State.initial(FRIENDS_COUNT)
    q = Queue()
    q.put(initial_state)
    path = explore_tree(q, 1500)
    for state in path:
        print(state)


if __name__ == '__main__':
    main()
