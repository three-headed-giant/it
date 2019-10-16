def func():
    while True:
        try:
            return self[next(self._onetime_keys)]
        except StopIteration:
            return None
        except KeyError:
            continue
