from __future__ import annotations
from student_group import StudentGroup
from dataclasses import dataclass
from dataclasses import field

BIKE_CAPACITY = 2


@dataclass(frozen=True)
class State:
    pizzeria: StudentGroup
    bike: StudentGroup = StudentGroup.empty()
    pub: StudentGroup = StudentGroup.empty()
    bike_position: str = 'pizzeria'
    parent: State | None = field(default=None, compare=False)

    def __str__(self):
        return f'{self.pizzeria}{self.bike}{self.pub} bike in: {self.bike_position}'

    def bike_elsewhere(self, source, destination):
        if self.bike_position in [source, destination]:
            return False
        return True

    def move_group(self, source_name: str, destination_name: str, group: StudentGroup) -> State:
        result_pizzera, result_bike, result_pub = self.pizzeria, self.bike, self.pub
        if source_name == 'bike':  # getting off the bike
            result_bike -= group
            if destination_name == 'pizzeria':
                result_pizzera += group
            else:
                result_pub += group
        else:  # mounting on the bike
            result_bike += group
            if source_name == 'pizzeria':
                result_pizzera -= group
            else:
                result_pub -= group
        if self.bike_position not in [source_name, destination_name]:
            result_bike_position = source_name if source_name != 'bike' else destination_name
        else:
            result_bike_position = self.bike_position
        return State(result_pizzera, result_bike, result_pub, result_bike_position, self)

    def generate_adjacents(self) -> set[State]:
        adjacents = set()
        source_destination = (('pizzeria', 'bike'), ('bike', 'pizzeria'), ('bike', 'pub'), ('pub', 'pizzeria'))
        for src_dest_pair in source_destination:
            source_name = src_dest_pair[0]
            destination_name = src_dest_pair[1]
            source: StudentGroup = getattr(self, source_name)

            if self.bike_elsewhere(source_name, destination_name) and self.bike == StudentGroup.empty():
                continue  # bike is elsewhere and nobody can bring it here

            for subgroup in source.generate_subgroups(max_size=BIKE_CAPACITY if destination_name == 'bike' else None):
                adjacent_candidate: State = self.move_group(source_name, destination_name, subgroup)
                if adjacent_candidate.is_valid():
                    adjacents.add(adjacent_candidate)
        return adjacents

    def is_valid(self) -> bool:
        if not self.pizzeria.is_valid():
            return False
        if not self.pub.is_valid():
            return False
        if self.bike.size() > BIKE_CAPACITY:
            return False
        return True

    def is_solution(self) -> bool:
        if self.pizzeria.size() != 0:
            return False
        if self.bike.size() != 0:
            return False
        return True

    def ancestor_states(self) -> list[State]:
        ancestors = []
        state: State | None = self
        while state:
            ancestors.append(state)
            state = state.parent
        ancestors.reverse()
        return ancestors

    @staticmethod
    def initial(number_of_students: int):
        pizzeria_group = StudentGroup.split_evenly(number_of_students)
        return State(pizzeria_group)
