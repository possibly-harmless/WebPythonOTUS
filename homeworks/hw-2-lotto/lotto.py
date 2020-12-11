from lotto import Lotto
from lotto.settings import DEFAULT_PLAYERS, MAX_PLAYERS, DEFAULT_CARD_SIZE, MAX_CARD_SIZE, MAX_NUMBER, DEFAULT_MAX_NUMBER
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
@click.option(
    "--cardsize",
    default=DEFAULT_CARD_SIZE,
    help=f"Число позиций в карточке. Не должно превышать {MAX_CARD_SIZE}"
)
@click.option(
    "--maxnum",
    default=DEFAULT_MAX_NUMBER,
    help=f"Максимальное число на боченке. Не должно превышать{MAX_NUMBER}"
)
def lotto_game(name, players, cardsize, maxnum):
    if len(set(name)) < len(name):
        print("Нельзя использовать повторяющиеся имена для игроков. Игра не может состояться.")
        return
    if players > MAX_PLAYERS:
        print(
            f"Превышено максимальное число игроков {MAX_PLAYERS}. Игра будет проходить с числом игроков {MAX_PLAYERS}"
        )
        players = MAX_PLAYERS
    Lotto(
        player_names=name,
        players=max(players, len(name)),
        card_size=cardsize,
        max_number=maxnum
    ).start_game()


if __name__ == "__main__":
    lotto_game()
