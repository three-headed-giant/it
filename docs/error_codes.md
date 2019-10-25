# Error codes

### DEFAULT_MUTABLE_ARG
Default argument is something mutable.

```py
def foo(x = []): ...
```
    
### CONTROL_FLOW_INSIDE_FINALLY
A return/break/continue that would implicitly cancel any active exception.

```py
def foo():
        try:
            foo()
        finally:
            return
```
    
### UNREACHABLE_EXCEPT
Except statement is unreachable due to a more broad except.

```py
try:
        raise ValueError
    except Exception:
        pass
    except ValueError:
        pass
```
    
### YIELD_FROM
`yield` can be replaced with `yield from`.

```py
for x in y:
        yield x
```
    to
```py
yield from y
```
    
### BUILTIN_ENUMERATE
`range(len(iterable))` can be replaced with `enumerate(iterable)`

```py
for index in range(len(iterable)):
        print(index, iterable[index])
```
    to
```py
for index, item in enumerate(iterable):
        print(index, item)
```
    
### OPTIONAL
`Union[Type, None]` can be replaced with `Optional[Type]`.

```py
def foo(x: Union[str, None]): ...
```
    to
```py
def foo(x: Optional[str]): ...
```
    
### SUPER_ARGS
`super(MyClass, self)` can be replaced with `super()`

```py
super(MyClass, self)
```
    to
```py
super()
```
    
### USE_COMPREHENSION
`list`/`dict`/`set` calls with a generator expression
    can be replaced with comprehensions.
    
```py
operands = list(b8(token) for token in tokens)
    patterns = dict((token.name, b8(token)) for token in tokens)
    unique_operands = set(b8(token) for token in tokens)
```
    to
```py
operands = [b8(token) for token in tokens]
    patterns = {token.name: b8(token) for token in tokens}
    unique_operands = {b8(token) for token in tokens}
```
    
### MAP_USE_COMPREHENSION
A map (to a complex callable) can be replaced with 
    `list` or `set` comprehensions.
    
```py
operands = list(map(itemgetter(0), tokens))
    unique_operands = set(map(attrgetter('unique_version'), tokens))
```
    to
```py
operands = [token[0] for token in tokens]
    unique_operands = {token.unique_version for token in tokens}
```
    
### ALPHABET_CONSTANT
A constant literal with the value of ASCII alphabet (`x = "ABC....Z"`) can be replaced 
    with `string.ascii_letters`/`string.ascii_uppercase`/`string.ascii_lowercase`
    
```py
GUESS_MY_NAME = "abcde...WXYZ"
    UPPERCASE_ALPH = "ABCD...WXYZ"
    LOWERCASE_ALPH = "abcd...wxyz"
    
    def game(char):
        return char in GUESS_MY_NAME
```
    to
```py
import string
    UPPERCASE_ALPH = string.ascii_uppercase
    LOWERCASE_ALPH = string.ascii_lowercase
    
    def game(char):
        return char in string.ascii_letters
```
    
### UNUSED_IMPORT
A module/name is imported but not used.
