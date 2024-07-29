from v2.components import Game, Team
from v2.solver import solve


def main():
    games = [Game(i) for i in range(1024)]
    teams = [Team(i) for i in range(12)]

    solve(games, teams)


if __name__ == '__main__':
    main()
