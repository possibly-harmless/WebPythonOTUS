from lotto import Lotto
from lotto.settings import DEFAULT_PLAYERS, MAX_PLAYERS
import click


@click.command()
@click.option(
    "--name",
    multiple=True,
    default=[],
    help="Имя игрока-человека. Повторяйте для каждого игрока в случае нескольких"
)
@click.option(
    "--players",
    default=DEFAULT_PLAYERS,
    help=f"Общее число игроков. Не должно превышать максимального числа игроков {MAX_PLAYERS}"
)
def lotto_game(name, players):
    if len(set(name)) < len(name):
        print("Нельзя использовать повторяющиеся имена для игроков. Игра не может состояться.")
        return
    if players > MAX_PLAYERS:
        print(
            f"Превышено максимальное число игроков {MAX_PLAYERS}. Игра будет проходить с числом игроков {MAX_PLAYERS}"
        )
        players = MAX_PLAYERS
    Lotto(player_names=name, players=players).start_game()


if __name__ == "__main__":
    lotto_game()
