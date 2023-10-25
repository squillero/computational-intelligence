from student_group import StudentGroup


def test_equality():
    first_group = StudentGroup(3, 4)
    second_group = StudentGroup(3, 4)
    assert first_group == second_group
    assert hash(first_group) == hash(second_group)


def test_add():
    first_group = StudentGroup(3, 4)
    second_group = StudentGroup(2, 0)
    res = first_group + second_group
    assert type(res) == type(first_group)
    assert res.ce == 5
    assert res.ds == 4


def test_add_empty_groups():
    first_group = StudentGroup(0, 0)
    second_group = StudentGroup(0, 0)
    res = first_group + second_group
    assert res.ce == 0
    assert res.ds == 0


def test_generate_sized_subgroups():
    group = StudentGroup(3, 4)
    subgroups = group.generate_sized_subgroups(3)
    expected_subgroups = {StudentGroup(0, 3), StudentGroup(1, 2), StudentGroup(2, 1), StudentGroup(3, 0)}
    assert len(expected_subgroups) == len(subgroups)
    for expected_subgroup in expected_subgroups:
        assert expected_subgroup in subgroups
