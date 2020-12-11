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
        pass

    @abstractmethod
    def get_height(self):
        pass

    @abstractmethod
    def compile(self, height=None, width=None):
        pass

    def draw(self):
        for row in self.compile():
            print(*row)


class RectangularBuildingBlock(RectangularFigure):

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
    def __init__(self,  *children, **kwargs):
        super().__init__(**kwargs)
        for child in children:
            child.parent = self
        self.children = children

    def padded_children(self, _):
        return self.children


class Row(Container):

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
