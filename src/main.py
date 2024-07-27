from datetime import datetime, timedelta

from components import ScheduledInput, PlayableTeamCollection, Field, Team, TimeSlotGenerator, CoachConflict
from solver import schedule

FIELD_ONE = Field(1, list(
    TimeSlotGenerator(
        datetime(2024, 7, 27, 8, 30),
        step=timedelta(hours=2),
        break_duration=timedelta(minutes=30),
        limit=11
    )
))

FIELD_TWO = Field(2, list(
    TimeSlotGenerator(
        datetime(2024, 7, 27, 8, 30),
        step=timedelta(hours=2),
        break_duration=timedelta(minutes=15),
        limit=12
    )
))

FIELD_THREE = Field(3, list(
    TimeSlotGenerator(
        datetime(2024, 7, 27, 8),
        step=timedelta(hours=1),
        break_duration=(timedelta(minutes=15), timedelta(minutes=30)),
        limit=12,
        concurrency=2,
    )
))

FIELD_FOUR = Field(4, list(
    TimeSlotGenerator(
        datetime(2024, 7, 27, 8, 30),
        step=timedelta(hours=1),
        break_duration=(timedelta(minutes=15), timedelta(minutes=30)),
        limit=12,
        concurrency=2,
    )
) + list(
    TimeSlotGenerator(
        datetime(2024, 7, 28, 8, 30),
        step=timedelta(hours=1),
        break_duration=(timedelta(minutes=15), timedelta(minutes=30)),
        limit=14,
        concurrency=2
    )
))

FIELD_FIVE = Field(5, list(
    TimeSlotGenerator(
        datetime(2024, 7, 27, 8),
        step=timedelta(hours=1),
        break_duration=(timedelta(minutes=5), timedelta(minutes=30)),
        limit=12,
        concurrency=2,
    )
) + list(
    TimeSlotGenerator(
        datetime(2024, 7, 28, 8),
        step=timedelta(hours=1),
        break_duration=(timedelta(minutes=5), timedelta(minutes=30)),
        limit=14,
        concurrency=2
    )
))

TEAM_GROUP_ONE = PlayableTeamCollection([Team(i) for i in range(1, 6)])
TEAM_GROUP_TWO = PlayableTeamCollection([Team(i) for i in range(6, 13)])

COACH_CONFLICT_ONE = CoachConflict(1, [Team(2), Team(7)])
COACH_CONFLICT_TWO = CoachConflict(2, [Team(4), Team(9)])


def main():
    schedule_input = ScheduledInput(1) \
        .with_fields([FIELD_ONE, FIELD_TWO, FIELD_THREE, FIELD_FOUR, FIELD_FIVE]) \
        .with_team_groups([TEAM_GROUP_ONE, TEAM_GROUP_TWO]) \
        .with_coach_conflicts([COACH_CONFLICT_ONE, COACH_CONFLICT_TWO])

    schedule(schedule_input)


if __name__ == '__main__':
    main()
