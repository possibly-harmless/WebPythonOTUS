from .core import RectangularFigure, Column, Row, VerticalAlignment, HorizontalAlignment, \
    RectangularBuildingBlock
from functools import lru_cache


class HorizontalSeparator(RectangularFigure):
    """
    Примитив вертикальной линии - разделителя (то есть, разделитель по горизонтали).
    """
    def __init__(self, separator, **kwargs):
        super().__init__(**kwargs)
        self.separator = separator

    def get_height(self):
        return None

    def get_width(self):
        return 1

    def compile(self, height=None, width=None):
        assert height
        return [[self.separator]] * height


class VerticalSeparator(RectangularFigure):
    """
    Примитив горизонтальной линии - разделителя (то есть, разделитель по вертикали).
    """
    def __init__(self, separator, **kwargs):
        super().__init__(**kwargs)
        self.separator = separator

    def get_height(self):
        return 1

    def get_width(self):
        return None

    def compile(self, height=None, width=None):
        assert width
        return [[self.separator] * width]


class VerticalPadding(RectangularBuildingBlock):
    """
    Контейнер, реализующий padding по вертикали до заданной общей высоты.
    """
    def __init__(self, inner, total_height=None, **kwargs):
        super().__init__(**kwargs)
        assert isinstance(inner, RectangularFigure)
        self.total_height = 0 if total_height is None else total_height
        self.alignment = self.vert_align or inner.vert_align
        self.padding = self.padding or inner.padding
        inner.parent = self
        self.inner = inner

    def get_current_figure(self, height=None, width=None):
        if height and self.total_height < 0:
            full_height = height + self.total_height
        elif width and not self.total_height:
            full_height = height
        else:
            full_height = self.total_height
        pad_height = full_height - self.inner.get_height()
        if pad_height <= 0:
            return self.inner
        else:
            if self.alignment is VerticalAlignment.TOP:
                top = 0
            elif self.alignment is VerticalAlignment.CENTER:
                top = int(pad_height / 2)
            else:
                top = pad_height
            bottom = pad_height - top
            return Column(
                *([VerticalSeparator(self.padding)] * top),
                self.inner,
                *([VerticalSeparator(self.padding)] * bottom)
            )


class HorizontalPadding(RectangularBuildingBlock):
    """
    Контейнер, реализующий padding по горизонтали до заданной общей ширины.
    """
    def __init__(self, inner, total_width=None, **kwargs):
        super().__init__(**kwargs)
        assert isinstance(inner, RectangularFigure)
        self.total_width = 0 if total_width is None else total_width
        self.alignment = self.hor_align or inner.hor_align
        self.padding = self.padding or inner.padding
        inner.parent = self
        self.inner = inner

    def get_current_figure(self, height=None, width=None):
        if width and self.total_width < 0:
            full_width = width + self.total_width
        elif width and not self.total_width:
            full_width = width
        else:
            full_width = self.total_width
        pad_width = full_width - self.inner.get_width()
        if pad_width <= 0:
            return self.inner
        else:
            if self.alignment is HorizontalAlignment.LEFT:
                left = 0
            elif self.alignment is HorizontalAlignment.CENTER:
                left = int(pad_width / 2)
            else:
                left = pad_width
            right = pad_width - left
            return Row(
                *([HorizontalSeparator(self.padding)] * left),
                self.inner,
                *([HorizontalSeparator(self.padding)] * right)
            )


class PaddableRow(Row):
    """
    Вариант Row с неопределенной высотой, определяющейся высотой максимально высокого
    дочернего элемента.
    """
    def get_height(self):
        heights = list({c.get_height() for c in self.children} - {None})
        assert heights
        return max(heights)

    def padded_children(self, height):
        return list(map(
            lambda child: VerticalPadding(child, height, vert_align=self.vert_align),
            self.children
        ))


class PaddableColumn(Column):
    """
    Вариант Column с неопределенной шириной, определяющейся шириной максимально широкого
    дочернего элемента.
    """
    def get_width(self):
        widths = list({c.get_width() for c in self.children} - {None})
        assert widths
        return max(widths)

    def padded_children(self, width):
        return list(map(
            lambda child: HorizontalPadding(child, width, hor_align=self.hor_align),
            self.children
        ))


class TextLine(RectangularFigure):
    """
    Примитив одной строки текста.
    """
    def __init__(self, text: str, **kwargs):
        super().__init__(**kwargs)
        self.text = text

    def get_height(self):
        return 1

    def get_width(self):
        return len(self.text)

    def compile(self, height=None, width=None):
        return [list(self.text)]


class Text(RectangularBuildingBlock):
    """
    Примитив многострочного текста.
    """
    def __init__(self, textlines, **kwargs):
        super().__init__(**kwargs)
        self.lines = textlines

    @lru_cache()
    def get_current_figure(self, height=None, width=None):
        return PaddableColumn(
            *map(lambda text: TextLine(text), self.lines),
            hor_align=self.hor_align
        )
