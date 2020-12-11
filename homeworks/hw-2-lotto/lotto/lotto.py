from console import RectangularBuildingBlock, Column, VerticalSeparator, Row, HorizontalSeparator, \
    HorizontalPadding, HorizontalAlignment, Text, PaddableColumn
from .players import User, Dealer
from .settings import DEFAULT_CARD_SIZE, DEFAULT_PLAYERS, USER_NAMES, DEFAULT_MAX_NUMBER
from .utils import is_int_str, cls
from operator import itemgetter
import random


class Messages(RectangularBuildingBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = []

    def add_message(self, msg):
        self.messages.append(msg)

    def clear_messages(self):
        self.messages = []

    def get_current_figure(self, height=None, width=None):
        return Column(
            VerticalSeparator("="),
            Row(
                HorizontalSeparator("="),
                HorizontalPadding(
                    Text(
                        [" "] + self.messages + [" "],
                        hor_align=HorizontalAlignment.LEFT
                    ),
                    30
                ),
                HorizontalSeparator("=")
            ),
            VerticalSeparator("="),
            hor_align=HorizontalAlignment.LEFT
        )


class Lotto(RectangularBuildingBlock):
    def __init__(
            self,
            card_size=DEFAULT_CARD_SIZE,
            max_number=DEFAULT_MAX_NUMBER,
            players=DEFAULT_PLAYERS,
            player_names=(),
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.dealer = Dealer(card_size, max_number)
        self.nonhumans = [User(n, self) for n in random.sample(USER_NAMES, players - len(player_names))]
        self.humans = [User(name, self) for name in player_names]
        self.abbreviations = {chr(ord('A')+index): player for index, player in enumerate(self.humans)}
        self.messages = Messages()
        self.done = False
        self.last_played = None
        all_users = self.nonhumans + self.humans
        for user in all_users:
            user.get_card(self.dealer)

    def get_current_figure(self, height=None, width=None):
        components = [*self.nonhumans, *self.humans]
        if self.messages.messages:
            components.append(self.messages)
        return PaddableColumn(*components, hor_align=HorizontalAlignment.LEFT)

    def repaint(self):
        cls()
        self.draw()
        self.messages.clear_messages()

    def request_new_number(self):
        num = self.dealer.next_number()
        if num is None:
            self.messages.add_message("Бочонков больше нет. Игра окончена!")
            self.done = True
        else:
            self.last_played = num
            for player in self.nonhumans:
                player.mark_used_number_if_present(num)
            self.messages.add_message(f"Новый бочонок: {num}")
        self.repaint()
        self.detect_winners()

    def handle_user_action(self, action):
        action_type, user = itemgetter("action", "user")(action)
        if action_type == "MARK_POSITION":
            card, position = itemgetter("card", "position")(action)
            if not self.dealer.check_card(card):
                self.messages.add_message(f"Игрок {user.name} пытался сжульничать и был удален из игры!")
                self.humans = [u for u in self.humans if u is not user]
                if not self.humans and not self.nonhumans:
                    self.messages.add_message("")
                    self.messages.add_message("Все игроки были удалены за жульничество!")
                    self.messages.add_message("")
                    self.messages.add_message("Игра окончена. Победителей нет.")
                    self.done = True
        self.repaint()

    def detect_winners(self):
        winners = [user for user in self.nonhumans + self.humans if user.card.is_complete()]
        if not winners:
            return
        for h in self.humans:
            if h not in winners and not bool(h.card.get_unmarked() - {self.last_played}):
                return  # Игрок еще может закрыть последнюю позицию и стать одним из победителей
        self.done = True
        if len(winners) == 1:
            self.messages.add_message("Победителем становится")
            self.messages.add_message("")
            self.messages.add_message(winners[0].name.upper())
        else:
            self.messages.add_message("Победителями стали:")
            self.messages.add_message("")
            for w in winners:
                self.messages.add_message(w.name.upper())
        self.messages.add_message("")
        self.messages.add_message("Игра окончена!")
        self.repaint()

    def mark_position(self, player, position):
        player.mark_used_position(position)
        self.detect_winners()

    def remind_last_number(self):
        msg = ("Ни одного бочонка еще не объявляли" if self.last_played is None
               else f"Последний объявленный бочонок был: {self.last_played}")
        self.messages.add_message(msg)
        self.repaint()

    def quit(self):
        self.messages.add_message("Игра остановлена по запросу пользователя")
        self.repaint()
        self.done = True

    def start_game(self):
        self.repaint()
        while not self.done:
            player_choices = "\t\t"+"\n\t\t".join(
                [f"{abbr} - {player.name}" for abbr, player in self.abbreviations.items()]
            )
            val = input(
                "Сделайте выбор:"
                "\n\tn - Объявить следующий бочонок"
                "\n\tp - Напомнить последний объявленный бочонок"
                "\n\t<имя игрока> <позиция>, где <имя игрока> (аббревиатура на английском: A, B, etc.)" 
                f":\n {player_choices}," 
                "\n\ta позиция - позиция бочонка на карте, целое число: 1, 2, 3, 4, etc, напр.: А 2"
                "\n\tq - Завершить игру"
                "\n>>>"
            )
            if val == 'n':
                self.request_new_number()
            elif any([val.startswith(abb) for abb in self.abbreviations.keys()]):
                abb = val[0]
                pstr = val[1:].strip()
                if is_int_str(pstr):
                    self.mark_position(self.abbreviations[abb], int(pstr))
                else:
                    self.messages.add_message("Позиция на карте должна быть целым числом")
            elif val == 'p':
                self.remind_last_number()
            elif val == 'q':
                self.quit()
            else:
                self.messages.add_message("Введена неверная опция. Попробуйте еще раз")
                self.repaint()
