from .components import Team, Game
from ortools.sat.python import cp_model


def solve(games: list[Game], teams: list[Team]):
    model = cp_model.CpModel()

    game_team_assignments = {}

    for game in games:
        for home_team in teams:
            for away_team in teams:
                key = (game.id, home_team.id, away_team.id)
                if home_team.id == away_team.id:
                    game_team_assignments[key] = model.new_constant(0)
                else:
                    label = f'teams {home_team.id}v{away_team.id} at game {game.id}'
                    game_team_assignments[key] = model.new_bool_var(label)

    at_home = {}

    for game in games:
        for team in teams:
            at_home[(game.id, team.id)] = model.new_bool_var(f'is {team.id} home at game {game.id}')

    for game in games:
        for home_team in teams:
            possible_opponents = []

            for away_team in teams:
                if home_team.id == away_team.id:
                    continue

                possible_opponents.append(game_team_assignments[(game.id, home_team.id, away_team.id)])
                possible_opponents.append(game_team_assignments[(game.id, away_team.id, home_team.id)])

            model.add(sum(possible_opponents) == 1)

    for game in games:
        for home_team in teams:
            for away_team in teams:
                if home_team.id == away_team.id:
                    continue

                model.add_implication(game_team_assignments[(game.id, home_team.id, away_team.id)],
                                      at_home[(game.id, home_team.id)])
                model.add_implication(~game_team_assignments[(game.id, home_team.id, away_team.id)],
                                      at_home[(game.id, away_team.id)])

    # for team in teams:
    #     for game_index in range(len(games) - 2):
    #         game1, game2, game3 = games[game_index:game_index + 3]
    #
    #         model.add_bool_or([
    #             at_home[(game1.id, team.id)],
    #             at_home[(game2.id, team.id)],
    #             at_home[(game3.id, team.id)]
    #         ])
    #         model.add_bool_or([
    #             ~at_home[(game1.id, team.id)],
    #             ~at_home[(game2.id, team.id)],
    #             ~at_home[(game3.id, team.id)]
    #         ])

    breaks = []

    for team in teams:
        for game_index in range(len(games) - 1):
            game1, game2 = games[game_index:game_index + 2]

            break_var = model.new_bool_var(f'Break var for {team.id} (games {game1.id} & {game2.id})')
            model.add_bool_or(~at_home[(game1.id, team.id)], ~at_home[(game2.id, team.id)], break_var)
            model.add_bool_or(at_home[game1.id, team.id], at_home[game2.id, team.id], break_var)
            model.add_bool_or(~at_home[game1.id, team.id], at_home[game2.id, team.id], ~break_var)
            model.add_bool_or(at_home[game1.id, team.id], ~at_home[game2.id, team.id], ~break_var)

            breaks.append(break_var)

    model.add(sum(breaks) >= 2 * len(teams) - 4)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Yay!")
    else:
        print("Nay", status)
