from console import Row, Digit, HorizontalSeparator, RectangularBuildingBlock, \
    Column, VerticalSeparator


class CardNumber(RectangularBuildingBlock):

    def __init__(self, number, **kwargs):
        super().__init__(**kwargs)
        assert type(number) is int and 0 < number < 100
        self.high = int(number / 10)
        self.low = number % 10

    def get_current_figure(self, height=None, width=None):
        return Row(
            Digit.get(self.high),
            HorizontalSeparator(" "),
            Digit.get(self.low)
        )


class UsedCardNumber(CardNumber):
    def __init__(self, number, **kwargs):
        super().__init__(number, **kwargs)

    def compile(self, height=None, width=None):
        compiled = super().compile(height=height, width=width)
        return list(map(
            lambda row: list(map(
                lambda elem: elem if elem != ' ' else "/",
                row
            )),
            compiled
        ))


class Card(RectangularBuildingBlock):
    """
    Класс реализующий логику и отображение в консоли для одного билета
    """
    def __init__(self, dealer, card_numbers, **kwargs):
        super().__init__(**kwargs)
        for num in card_numbers:
            assert type(num) is int and 0 < num < 100
        self.dealer = dealer
        self.numbers = card_numbers
        self.used = set()

    def mark_used_position(self, position: int):
        """
        Закрывает данное поле / число в билете. Если позиция не соответствует
        последнему сыгранному числу, то это жульничание
        """
        assert 0 < position <= len(self.numbers)
        self.used.add(self.numbers[position - 1])

    def mark_used_number_if_present(self, num: int):
        """
        Закрывает число в билете при условии что оно в нем содержится
        """
        if num in self.numbers:
            self.used.add(num)

    def get_unmarked(self):
        """
        :return: множество (set) всех еще не закрытых чисел в билете
        """
        return set(self.numbers) - self.used

    def is_complete(self):
        """
        :return: True если билет полностью закрыт / сыгран, False в противном случае
        """
        return not bool(self.get_unmarked())

    def get_current_figure(self, height=None, width=None):
        """
        Отображение билета в консоли
        """
        def get_components():
            yield HorizontalSeparator("|")
            for num in self.numbers:
                yield HorizontalSeparator(" ")
                yield UsedCardNumber(num) if num in self.used else CardNumber(num)
                yield HorizontalSeparator(" ")
                yield HorizontalSeparator("|")

        return Column(
            VerticalSeparator("-"),
            Row(*get_components()),
            VerticalSeparator("-")
        )
