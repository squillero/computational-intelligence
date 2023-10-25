from state import State
from student_group import StudentGroup


def test_equality():
    s = State.initial(4)
    other = State.initial(4)
    assert s == other


def test_bike_elsewhere_true():
    s = State.initial(6)
    assert s.bike_position == 'pizzeria'
    assert s.bike_elsewhere('bike', 'pub') == True
    assert s.bike_elsewhere('pub', 'bike') == True


def test_bike_elsewhere_false():
    s = State.initial(8)
    assert s.bike_position == 'pizzeria'
    assert s.bike_elsewhere('bike', 'pizzeria') == False
    assert s.bike_elsewhere('pizzeria', 'bike') == False


def test_move_group():
    s = State.initial(8)
    group = StudentGroup.split_evenly(4)
    state_after_movement = s.move_group('pizzeria', 'bike', group)
    assert state_after_movement == State(StudentGroup(2, 2), StudentGroup(2, 2))


def test_ancestor_states():
    parent = State(StudentGroup(0, 0), StudentGroup(2, 0), StudentGroup(1, 3), 'pizzeria')
    child = parent.move_group('bike', 'pub', StudentGroup(2, 0))
    ancestors = child.ancestor_states()
    assert ancestors is not None
    assert len(ancestors) == 2
    assert child in ancestors
    assert parent in ancestors
