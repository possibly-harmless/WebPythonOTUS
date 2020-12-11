from console import RectangularBuildingBlock, PaddableRow, HorizontalPadding, HorizontalAlignment, Text
from .card import Card
from .settings import DEFAULT_MAX_NUMBER
import random


class Dealer(object):
    """
    Сущность ведущего игры
    """
    def __init__(self, card_size: int, max_number: int = DEFAULT_MAX_NUMBER):
        self.card_size = card_size
        self.max_number = max_number
        self.available = list(range(1, self.max_number))
        self.used = set()

    def deal_card(self):
        """
        Выдать новую карту
        :return:
        """
        return Card(self, random.sample(range(1, self.max_number), self.card_size))

    def next_number(self):
        """
        Достать / объявить новый бочонок, или None, если они закончились
        :return:
        """
        if not self.available:
            return None
        num = random.choice(self.available)
        self.available.remove(num)
        self.used.add(num)
        return num

    def check_card(self, card: Card):
        """
        Проверить что на карте нет закрытых позиций для бочонков, которые
        еще не были объявлены
        :param card:
        :return:
        """
        return not bool(card.used - self.used)


class User(RectangularBuildingBlock):
    """
    Класс реализующий функционал игрока (человека или компьютера)
    """
    def __init__(self, name, game, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.game = game
        self.card = None

    def get_card(self, dealer: Dealer):
        self.card = dealer.deal_card()

    def mark_used_number_if_present(self, num):
        self.card.mark_used_number_if_present(num)

    def mark_used_position(self, position):
        """
        Закрыть позицию (правильно или сжульничать)
        :param position:
        :return:
        """
        self.card.mark_used_position(position)
        self.game.handle_user_action({
            "action": "MARK_POSITION",
            "user": self,
            "card": self.card,
            "position": position
        })

    def get_current_figure(self, height=None, width=None):
        """
        Отображение информации об игроке - имя и текущее состояние карты / билета
        :param height:
        :param width:
        :return:
        """
        return PaddableRow(
            HorizontalPadding(
                Text(["  Player", "  ", "  "+self.name.upper()], hor_align=HorizontalAlignment.LEFT),
                15,
                hor_align=HorizontalAlignment.LEFT
            ),
            self.card
        )
