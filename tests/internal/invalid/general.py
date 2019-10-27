ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class Foo(SomeObjects):
    def bar(self, x=[], y: Union[int, None] = None):
        x.append(1)
        for _ in range(3):
            try:
                super(bla, bla).foo_baz()
            except Exception:
                print("An exception")
            except AttributeError:
                print("An attribute error")
            finally:
                continue

        my_iterable = list(token[0] for token in tokens)
        for a in my_iterable:
            yield a

        my_other_iterable = list(map(itemgetter(0), tokens))
        for a in range(len(my_other_iterable)):
            print(a, "=>", my_other_iterable[a])
