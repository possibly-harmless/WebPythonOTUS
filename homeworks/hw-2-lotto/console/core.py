from abc import ABC, abstractmethod
from functools import reduce
from operator import add
from enum import Enum


class VerticalAlignment(Enum):
    TOP = 1
    CENTER = 2
    BOTTOM = 3


class HorizontalAlignment(Enum):
    LEFT = 1
    CENTER = 2
    RIGHT = 3


class RectangularFigure(ABC):
    """
    Базовый абстрактный класс для отображения прямоугольного блока в консоли
    """
    def __init__(
            self,
            horizontally_paddable=True,
            vertically_paddable=True,
            vert_align=VerticalAlignment.CENTER,
            hor_align=HorizontalAlignment.CENTER,
            padding=' ',
            parent=None
    ):
        self.horizontally_paddable = horizontally_paddable
        self.vertically_paddable = vertically_paddable
        self.vert_align = vert_align
        self.hor_align = hor_align
        self.padding = padding
        self.parent = parent

    @abstractmethod
    def get_width(self):
        """
        Ширина блока в символах
        :return:
        """
        pass

    @abstractmethod
    def get_height(self):
        """
        Высота блока в строках
        :return:
        """
        pass

    @abstractmethod
    def compile(self, height=None, width=None):
        """
        Метод для компиляции элемента в строки вывода консоли
        :param height:
        :param width:
        :return: Прямоугольный список списков символов. Внутренние списки символов -
        отдельные строки консольного вывода. Внешний список - вся совокупность этих
        строк
        """
        pass

    def draw(self):
        """
        Вывод элементов в консоль.
        :return:
        """
        for row in self.compile():
            print(*row)


class RectangularBuildingBlock(RectangularFigure):
    """
    Этот класс нужен для того, чтобы реализовывать динамически меняющиеся
    (изменяемые) фигуры. Если, например, мы имеем класс с изменяемым состоянием,
    то он должен реализовать метод get_current_figure(), который динамически
    генерирует прямоугольную фигуру - которая будет пересоздаваться каждый раз
    при вызове этого метода. Все остальные методы - делегирование к методам
    этой динамической фигуры.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @abstractmethod
    def get_current_figure(self, height=None, width=None):
        pass

    def get_width(self):
        return self.get_current_figure().get_width()

    def get_height(self):
        return self.get_current_figure().get_height()

    def compile(self, height=None, width=None):
        return self.get_current_figure(height=height, width=width).compile(height=height, width=width)


class Container(RectangularFigure, ABC):
    """
    Класс, который добавляет поля дочерних и родительских элементов.
    Дочерние элементы передаются прямо в конструктор.
    """
    def __init__(self,  *children, **kwargs):
        super().__init__(**kwargs)
        for child in children:
            child.parent = self
        self.children = children

    def padded_children(self, _):
        return self.children


class Row(Container):
    """
    Этот класс реализует примитив "строки" - то есть горизонтального контейнера.
    """
    def get_height(self):
        heights = list({c.get_height() for c in self.children} - {None})
        assert len(heights) <= 1
        return heights[0] if heights else None

    def get_width(self):
        result = 0
        for c in self.children:
            w = c.get_width()
            assert w is not None
            result += w
        return result

    def compile(self, height=None, width=None):
        if self.get_height():
            height = self.get_height()
        assert height
        return reduce(
            lambda fst, sec: [add(*full) for full in zip(fst, sec)],
            map(
                lambda elem: elem.compile(height=height, width=width),
                self.padded_children(height)
            )
        )


class Column(Container):
    """
    Этот класс реализует примитив "столбца" - то есть вертикального контейнера.
    """
    def get_width(self):
        widths = list({c.get_width() for c in self.children} - {None})
        assert len(widths) <= 1
        return widths[0] if widths else None

    def get_height(self):
        result = 0
        for c in self.children:
            h = c.get_height()
            assert h is not None
            result += h
        return result

    def compile(self, height=None, width=None):
        if self.get_width():
            width = self.get_width()
        assert width
        return reduce(
            add,
            map(
                lambda elem: elem.compile(height=height, width=width),
                self.padded_children(width)
            )
        )
