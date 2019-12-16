# Error codes

### DEFAULT_MUTABLE_ARG
Default argument is something mutable.

```py
def foo(x = []): ...
```
    
### YIELD_FROM
`yield` can be replaced with `yield from`.
### BUILTIN_ENUMERATE
`range(len(iterable))` can be replaced with `enumerate(iterable)`
### OPTIONAL
`Union[Type, None]` can be replaced with `Optional[Type]`.
### SUPER_ARGS
`super(MyClass, self)` can be replaced with `super()`
### USE_COMPREHENSION
`list`/`dict`/`set` calls with a generator expression
    can be replaced with comprehensions.
### MAP_USE_COMPREHENSION
A map (to a complex callable) can be replaced with 
    `list` or `set` comprehensions.
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
    
### SUPPRESS
A try statement with one except which only passes can be 
    replaced with `contextlib.suppress`
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
    
