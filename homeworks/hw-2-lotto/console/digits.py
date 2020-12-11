from .core import RectangularFigure

# Матрицы отображения цифр

DIGITS = [
    [
        [0, 1, 0],
        [1, 0, 1],
        [1, 0, 1],
        [1, 0, 1],
        [0, 1, 0]
    ],
    [
        [0, 1, 0],
        [1, 1, 0],
        [0, 1, 0],
        [0, 1, 0],
        [0, 1, 0]
    ],
    [
        [1, 1, 1],
        [0, 0, 1],
        [0, 1, 0],
        [1, 0, 0],
        [1, 1, 1]
    ],
    [
        [1, 1, 1],
        [0, 0, 1],
        [1, 1, 1],
        [0, 0, 1],
        [1, 1, 1]
    ],
    [
        [1, 0, 1],
        [1, 0, 1],
        [1, 1, 1],
        [0, 0, 1],
        [0, 0, 1]
    ],
    [
        [1, 1, 1],
        [1, 0, 0],
        [1, 1, 1],
        [0, 0, 1],
        [1, 1, 1]
    ],
    [
        [1, 1, 1],
        [1, 0, 0],
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1]
    ],
    [
        [1, 1, 1],
        [0, 0, 1],
        [0, 1, 0],
        [1, 0, 0],
        [1, 0, 0]
    ],
    [
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1]
    ],
    [
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
        [0, 0, 1],
        [1, 1, 1]
    ]
]


class Digit(RectangularFigure):
    """
    Класс для отображения цифры
    """
    @staticmethod
    def digit_to_chars(matrix):
        return [['#' if dig else ' ' for dig in row] for row in matrix]

    def __init__(self, digit_matrix):
        super().__init__()
        assert digit_matrix
        self.matrix = Digit.digit_to_chars(digit_matrix)

    def get_width(self):
        return len(self.matrix[0])

    def get_height(self):
        return len(self.matrix)

    def compile(self, height=None, width=None):
        return self.matrix  # Ignore height and width coming from upstream

    @staticmethod
    def get(digit):
        assert type(digit) is int and 0 <= digit <= 9
        return Digit(DIGITS[digit])
