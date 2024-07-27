from components import ScheduledInput, ScheduledOutput
from ortools.sat.python import cp_model


def schedule(schedule_input: ScheduledInput) -> ScheduledOutput:
    model = cp_model.CpModel()

    time_slots = {}

    for team in schedule_input.teams():
        for field in schedule_input.fields:
            field_suffix = f"_F{field.unique_id}"

            for time_slot in field.time_slots:
                interval_var = model.new_interval_var(start=time_slot.start_time.timestamp(),
                                                      end=time_slot.end_time.timestamp(),
                                                      name=f"t{time_slot.unique_id}{field_suffix}")
                pass

        for time_slot in schedule_input.time_slots():
            label = f"timeslot_T{team.unique_id}_Z{time_slot.unique_id}"
            time_slots[(team.unique_id, time_slot.unique_id)] = model.new_bool_var(label)

    return None
