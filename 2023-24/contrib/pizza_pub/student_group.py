from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class StudentGroup:
    ce: int
    ds: int

    def __add__(self, other):
        ce = self.ce + other.ce
        ds = self.ds + other.ds
        return StudentGroup(ce, ds)

    def __sub__(self, other):
        ce = self.ce - other.ce
        ds = self.ds - other.ds
        if ce < 0 or ds < 0:
            raise ValueError('Not enough students to subtract subgroup')
        return StudentGroup(ce, ds)

    def __str__(self):
        return f'({self.ce}, {self.ds})'

    def is_valid(self):
        if self.ds == 0:
            return True
        if self.ds >= self.ce:
            return True
        return False

    def generate_sized_subgroups(self, size: int) -> set[StudentGroup]:
        subgroups = set()
        max_ce = min(size, self.ce)
        for ce in range(max_ce + 1):
            if ce + self.ds < size:
                continue
            ds = size - ce
            subgroups.add(StudentGroup(ce, ds))
        return subgroups

    def generate_subgroups(self, max_size: int | None) -> set[StudentGroup]:
        subgroups = set()
        max_size = min(max_size, self.size()) if max_size else self.size()
        for subgroup_size in range(1, max_size + 1):
            sized_soubgroups = self.generate_sized_subgroups(subgroup_size)
            subgroups.update(sized_soubgroups)
        return subgroups

    def size(self) -> int:
        return self.ce + self.ds

    @staticmethod
    def empty():
        return StudentGroup(0, 0)

    @staticmethod
    def split_evenly(number_of_students):
        if number_of_students % 2 != 0:
            raise ValueError
        half_students = number_of_students // 2
        return StudentGroup(half_students, half_students)


"""     def __hash__(self):
        return hash((self.ce, self.ds))

    def __eq__(self, other):
        if not isinstance(other, StudentGroup):
            return False
        return self.__dict__ == other.__dict__

    def __init__(self, computer_engineers: int, data_scientists: int):
        if computer_engineers < 0 or data_scientists < 0: raise ValueError()
        self.ce = computer_engineers
        self.ds = data_scientists """
