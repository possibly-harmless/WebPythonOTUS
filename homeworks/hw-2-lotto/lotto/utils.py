def cls():
    print("\n" * 100)


def is_int_str(string):
    try:
        int(string)
        return True
    except ValueError:
        return False
