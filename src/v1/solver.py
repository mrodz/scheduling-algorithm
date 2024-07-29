import collections
import math

from components import ScheduledInput, ScheduledOutput, Field, TimeSlot, PlayableTeamCollection, Team
from ortools.sat.python import cp_model
from itertools import combinations
from typing import Union, Generator


def label_from_vars(field: Field, time_slot: TimeSlot, team_group: PlayableTeamCollection, team_one: Team,
                    team_two: Team) -> str:
    return f'field_{field.unique_id}_timeslot_{time_slot.unique_id}_group_{team_group.unique_id}_game_{team_one.unique_id}v{team_two.unique_id}'


def calculate_min_games(number_of_timeslots: int, number_of_teams: int) -> float:
    """
    Games for each team to play each other once:
    `A` = ncr(`number_of_teams`, 2) / `number_of_teams`

    `number_of_timeslots` / `A`
    """

    return (2 * number_of_timeslots) / (number_of_teams - 1)


def pick_team_against_remaining(teams: list[Team]) -> Generator[tuple[Team, list[Team]], None, None]:
    for i in range(len(teams)):
        team = teams[i]
        remaining = [x for j, x in enumerate(teams) if j != i]
        yield team, remaining


def schedule(schedule_input: ScheduledInput) -> ScheduledOutput:
    model = cp_model.CpModel()

    assigned_time_slot = collections.namedtuple('assigned_time_slot', 'field_id assignment_var interval')

    """
    Define the variables
    """

    assignments = {}
    team_to_intervals = collections.defaultdict(list)
    field_to_intervals = collections.defaultdict(list)

    for field in schedule_input.fields:
        for time_slot in field.time_slots:
            start = int(time_slot.start_time.timestamp())
            end = int(time_slot.end_time.timestamp())

            interval_var = model.new_fixed_size_interval_var(start=start,
                                                             size=end - start,
                                                             name=f"t{time_slot.unique_id}_F{field.unique_id}")

            field_to_intervals[field.unique_id].append(interval_var)

            for team_group in schedule_input.team_groups:
                for team_one, team_two in combinations(team_group.teams, 2):
                    # Order: field, time slot, team group, team 1, team 2
                    variable_name = label_from_vars(field, time_slot, team_group, team_one, team_two)

                    assignment_var = model.new_bool_var(variable_name)

                    key = (
                        field.unique_id,
                        time_slot.unique_id,
                        team_group.unique_id,
                        team_one.unique_id,
                        team_two.unique_id
                    )

                    assignments[key] = assignment_var

                    team_to_intervals[team_one.unique_id].append(interval_var)
                    team_to_intervals[team_two.unique_id].append(interval_var)

    """
    Define the constraints
    """

    # floored to allow for uneven distributions with a +/- 1 game count tolerance
    min_games_per_team = math.floor(calculate_min_games(schedule_input.timeslot_len(), schedule_input.teams_len()))

    for team_group in schedule_input.team_groups:
        for team, other_teams in pick_team_against_remaining(team_group.teams):
            team_one_games_played: Union[cp_model.LinearExpr, int] = 0

            for field in schedule_input.fields:
                for time_slot in field.time_slots:
                    for other_team in other_teams:
                        # because of the way we set up the index with a combination, we need to check both possibilities

                        key_pos_1 = (
                            field.unique_id,
                            time_slot.unique_id,
                            team_group.unique_id,
                            team.unique_id,  # home
                            other_team.unique_id  # away
                        )

                        key_pos_2 = (
                            field.unique_id,
                            time_slot.unique_id,
                            team_group.unique_id,
                            other_team.unique_id,  # home
                            team.unique_id  # away
                        )

                        if key_pos_1 in assignments:
                            team_one_games_played += assignments[key_pos_1]
                        elif key_pos_2 in assignments:
                            team_one_games_played += assignments[key_pos_2]

                    model.add_no_overlap(field_to_intervals[field.unique_id])

            # FIRST CONSTRAINT: evenly distribute games
            model.add(min_games_per_team <= team_one_games_played)

            intervals_applied_to_team = team_to_intervals[team.unique_id]

            # SECOND CONSTRAINT: no overlapping schedules
            # THIS IS BROKEN: see https://stackoverflow.com/a/70494431/17267647
            # model.add_no_overlap(intervals_applied_to_team)

    # TODO

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Solution:")

        for field in schedule_input.fields:
            for time_slot in field.time_slots:
                for team_group in schedule_input.team_groups:
                    for team_one, team_two in combinations(team_group.teams, 2):
                        key = (
                            field.unique_id,
                            time_slot.unique_id,
                            team_group.unique_id,
                            team_one.unique_id,
                            team_two.unique_id
                        )

                        if assignments[key]:
                            print(f"Game at field {field} ({time_slot}) - {team_one} vs {team_two}")
    else:
        print("No solution found.")
