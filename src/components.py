"""
Data classes that correspond to the input given through protocol buffers
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
import random
from typing import Optional, Generator, Union


@dataclass
class Team:
    unique_id: int


@dataclass
class PlayableTeamCollection:
    teams: list[Team]


_timeslot_id_counter = 0


def timeslot_id():
    global _timeslot_id_counter
    _timeslot_id_counter += 1
    return _timeslot_id_counter


@dataclass
class TimeSlot:
    unique_id: int
    start_time: datetime
    end_time: datetime
    concurrency: int = 1

    def __init__(self, start_time: datetime, end_time: datetime, concurrency: Optional[int]):
        self.unique_id = timeslot_id()
        self.start_time = start_time
        self.end_time = end_time
        if concurrency is not None:
            self.concurrency = concurrency

    @staticmethod
    def with_duration(start_time: datetime, *, hours: int, minutes: int = 0,
                      concurrency: int = 1) -> 'TimeSlot':
        return TimeSlot(start_time, start_time + timedelta(hours=hours, minutes=minutes), concurrency)


@dataclass
class Field:
    unique_id: int
    time_slots: list[TimeSlot]


@dataclass
class TimeSlotGenerator:
    start: datetime
    step: timedelta
    break_duration: Union[timedelta, tuple[timedelta, timedelta]]
    limit: int = 0
    concurrency: int = 1

    def __iter__(self):
        return self

    def __next__(self):
        self.limit -= 1

        if self.limit <= 0:
            raise StopIteration

        start_of_game = self.start
        end_of_game = start_of_game + self.step

        if type(self.break_duration) is tuple:
            delta_start, delta_end = self.break_duration
            endpoint_1 = delta_start.total_seconds()
            endpoint_2 = delta_end.total_seconds()

            random_delta_seconds = random.randint(min(endpoint_1, endpoint_2), max(endpoint_1, endpoint_2))

            delta = timedelta(seconds=random_delta_seconds)
        else:
            delta = self.break_duration

        self.start = end_of_game + delta

        return TimeSlot(start_of_game, end_of_game, self.concurrency)

@dataclass
class Booking:
    home_team: Team
    away_team: Team


@dataclass
class Reservation:
    field: Field
    start: datetime
    end: datetime
    booking: Optional[Booking]


@dataclass
class CoachConflict:
    unique_id: int
    teams: list[Team]


@dataclass
class ScheduledInput:
    unique_id: int
    team_groups: list[PlayableTeamCollection]
    fields: list[Field]
    coach_conflicts: list[CoachConflict]

    def __init__(self, unique_id: int, *, fields: Optional[list[Field]] = None,
                 coach_conflicts: Optional[list[CoachConflict]] = None,
                 team_groups: Optional[list[PlayableTeamCollection]] = None):
        if team_groups is None:
            team_groups = []
        if coach_conflicts is None:
            coach_conflicts = []
        if fields is None:
            fields = []

        self.unique_id = unique_id
        self.fields = fields
        self.coach_conflicts = coach_conflicts
        self.team_groups = team_groups

    def with_team_groups(self, team_groups: list[PlayableTeamCollection]) -> 'ScheduledInput':
        self.team_groups = team_groups
        return self

    def with_fields(self, fields: list[Field]) -> 'ScheduledInput':
        self.fields = fields
        return self

    def with_coach_conflicts(self, coach_conflicts: list[CoachConflict]) -> 'ScheduledInput':
        self.coach_conflicts = coach_conflicts
        return self

    def teams(self) -> Generator[Team, None, None]:
        for team_group in self.team_groups:
            for team in team_group.teams:
                yield team

    def time_slots(self) -> Generator[TimeSlot, None, None]:
        for field in self.fields:
            for slot in field.time_slots:
                yield slot


@dataclass
class ScheduledOutput:
    unique_id: int
    reservations: list[Reservation]
