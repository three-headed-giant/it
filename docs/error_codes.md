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
    
### UNUSED_IMPORT
A module/name is imported but not used.
