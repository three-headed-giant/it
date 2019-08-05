try:
    int("a")
except Exception:
    print("ZeroDivisionError")
except TypeError:
    print("TypeError")


class UserDefined(BaseException):
    pass


try:
    int("a")
except UserDefined:
    print("TypeError")
except TypeError:
    print("AAA")
