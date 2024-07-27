import collections

from components import ScheduledInput, ScheduledOutput
from ortools.sat.python import cp_model
from itertools import permutations


def schedule(schedule_input: ScheduledInput) -> ScheduledOutput:
    model = cp_model.CpModel()

    assigned_time_slot = collections.namedtuple('assigned_time_slot', 'field_id assignment_var interval')

    """
    Define the variables
    """

    assignments = {}
    field_to_intervals = collections.defaultdict(list)

    for field in schedule_input.fields:
        field_suffix = f"_F{field.unique_id}"

        for time_slot in field.time_slots:
            start = int(time_slot.start_time.timestamp())
            end = int(time_slot.end_time.timestamp())

            interval_var = model.new_fixed_size_interval_var(start=start,
                                                             size=end - start,
                                                             name=f"t{time_slot.unique_id}{field_suffix}")

            for team_group in schedule_input.team_groups:
                for team_one, team_two in permutations(team_group.teams, 2):
                    # Order: field, time slot, team group, team 1, team 2
                    variable_name = f'field_{field.unique_id}_timeslot_{time_slot.unique_id}_group_{team_group.unique_id}_game_{team_one.unique_id}v{team_two.unique_id}'

                    assignment_var = model.new_bool_var(variable_name)

                    key = (
                        field.unique_id,
                        time_slot.unique_id,
                        team_group.unique_id,
                        team_one.unique_id,
                        team_two.unique_id
                    )

                    assignments[key] = assignment_var

                    field_to_intervals[field.unique_id].append(interval_var)

    """
    Define the constraints
    """

    # TODO

    raise NotImplementedError()
