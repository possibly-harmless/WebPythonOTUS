def cls():
    """
    Очистка экрана.
    :return:
    """
    print("\n" * 100)


def is_int_str(string):
    """
    Проверка что строка представляет целое число.
    :param string:
    :return:
    """
    try:
        int(string)
        return True
    except ValueError:
        return False
