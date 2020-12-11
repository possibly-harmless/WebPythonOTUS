from console import RectangularBuildingBlock, Column, VerticalSeparator, Row, HorizontalSeparator, \
    HorizontalPadding, HorizontalAlignment, Text, PaddableColumn
from .players import User, Dealer
from .settings import DEFAULT_CARD_SIZE, DEFAULT_PLAYERS, USER_NAMES
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
                )
                ,
                HorizontalSeparator("=")
            ),
            VerticalSeparator("="),
            hor_align=HorizontalAlignment.LEFT
        )


class Lotto(RectangularBuildingBlock):
    def __init__(
            self,
            card_size=DEFAULT_CARD_SIZE,
            players=DEFAULT_PLAYERS,
            name='You',
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.dealer = Dealer(card_size)
        self.others = [User(n, self) for n in random.sample(USER_NAMES, players - 1)]
        self.you = User(name, self)
        self.messages = Messages()
        self.done = False
        self.last_played = None
        all_users = self.others + [self.you]
        for user in all_users:
            user.get_card(self.dealer)

    def get_current_figure(self, height=None, width=None):
        components = [*self.others, self.you]
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
            self.messages.add_message("No numbers left to play. Game over!")
            self.done = True
        else:
            self.last_played = num
            for player in self.others:
                player.mark_used_number_if_present(num)
            self.messages.add_message("New number is %d" % num)
        self.repaint()
        self.detect_winners()

    def handle_user_action(self, action):
        action_type, user = itemgetter("action", "user")(action)
        if action_type is "MARK_POSITION":
            card, position = itemgetter("card", "position")(action)
            if not self.dealer.check_card(card):
                self.messages.add_message("Player %s tried to cheat!" % user.name)
                card.unmark_position(position)
        self.repaint()

    def detect_winners(self):
        winners = [user for user in self.others + [self.you] if user.card.is_complete()]
        if not winners:
            return
        if self.you not in winners and not bool(self.you.card.get_unmarked() - set([self.last_played])):
            return  # You still can join the winners by marking your last unmarked number
        self.done = True
        if len(winners) == 1:
            self.messages.add_message("The winner is %s" % winners[0].name)
        else:
            self.messages.add_message("The winners are:")
            for w in winners:
                self.messages.add_message(w.name)
        self.messages.add_message("Game over!")
        self.repaint()

    def mark_position(self, position):
        self.you.mark_used_position(position)
        self.detect_winners()

    def remind_last_number(self):
        msg = ("No number was played yet" if self.last_played is None
               else ("Last number played was %d" % self.last_played))
        self.messages.add_message(msg)
        self.repaint()

    def quit(self):
        self.messages.add_message("The game stopped at user's request")
        self.repaint()
        self.done = True

    def start_game(self):
        self.repaint()
        while not self.done:
            val = input(
                """Enter choice:
                 n - get next number
                 p - remind last played number
                 1, 2, 3, 4, ... - mark position as present on your card
                 q - quit the game
                 \n
                 """
            )
            if val == 'n':
                self.request_new_number()
            elif is_int_str(val):
                self.mark_position(int(val))
            elif val == 'p':
                self.remind_last_number()
            elif val == 'q':
                self.quit()
            else:
                self.messages.add_message("Unrecognized option")
                self.repaint()

