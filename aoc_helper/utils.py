import builtins
import functools
import itertools
import operator
import re
import typing
from collections import deque

T = typing.TypeVar("T")
U = typing.TypeVar("U")


def extract_ints(raw: str) -> typing.List[int]:
    """Utility function to extract all integers from some string.

    Many inputs can be directly parsed with this function.
    """
    return list(map(int, re.findall(r"((?:-|\+)?\d+)", raw)))


def chunk(
    iterable: typing.Iterable[T], chunk_size: int
) -> typing.Iterable[tuple[T, ...]]:
    """Utility function to chunk an iterable into chunks of a given size.

    If there are not enough elements in the iterable to fill the last chunk,
    the last chunk will be dropped.
    """
    return zip(*[builtins.iter(iterable)] * chunk_size)


def chunk_default(
    iterable: typing.Iterable[T], chunk_size: int, default: T
) -> typing.Iterable[tuple[T, ...]]:
    """Utility function to chunk an iterable into chunks of a given size.

    If there are not enough elements in the iterable to fill the last chunk,
    the missing elements will be replaced with the default value.
    """
    return itertools.zip_longest(
        *[builtins.iter(iterable)] * chunk_size, fillvalue=default
    )


class iter(typing.Generic[T]):
    _SENTINEL = object()

    def __init__(self, it: typing.Iterable[T]) -> None:
        self.it = builtins.iter(it)

    def __iter__(self) -> typing.Iterable[T]:
        return self.it.__iter__()

    def map(self, func: typing.Callable[[T], U]) -> "iter[U]":
        """Return an iterator containing the result of calling func on each
        element in this iterator.
        """
        return type(self)(map(func, self))

    def filter(self, pred: typing.Union[typing.Callable[[T], bool], None]) -> "iter[T]":
        """Return an iterator containing only the elements for which pred
        returns True.

        If pred is None, return an iterator containing only elements that are
        truthy.
        """
        return type(self)(filter(pred, self))

    @typing.overload
    def reduce(self, func: typing.Callable[[T, T], T]) -> T:
        ...

    @typing.overload
    def reduce(self, func: typing.Callable[[T, T], T], initial: T) -> T:
        ...

    @typing.overload
    def reduce(self, func: typing.Callable[[U, T], U], initial: U) -> U:
        ...

    def reduce(self, func, initial=_SENTINEL):
        """Reduce the iterator to a single value, using the reduction
        function provided.
        """
        if initial is self._SENTINEL:
            return functools.reduce(func, self)
        return functools.reduce(func, self, initial)

    @typing.overload
    def accumulate(self) -> "iter[T]":
        ...

    @typing.overload
    def accumulate(self, func: typing.Callable[[T, T], T]) -> "iter[T]":
        ...

    @typing.overload
    def accumulate(self, func: typing.Callable[[T, T], T], initial: T) -> "iter[T]":
        ...

    @typing.overload
    def accumulate(self, func: typing.Callable[[U, T], U], initial: U) -> "iter[U]":
        ...

    def accumulate(self, func=operator.add, initial=_SENTINEL):
        """Return the accumulated results of calling func on the elements in
        this iterator.

        initial is only usable on versions of Python equal to or greater than 3.8.
        """
        if initial is self._SENTINEL:
            return type(self)(itertools.accumulate(func, self))
        return type(self)(itertools.accumulate(func, self, initial))

    def foreach(self, func: typing.Callable[[T], typing.Any]) -> None:
        """Run func on every value in this iterator, immediately."""
        for el in self:
            func(el)

    def chunk(self, n: int) -> "iter[typing.Tuple[T, ...]]":
        """Return an iterator containing the elements of this iterator in chunks
        of size n. If there are not enough elements to fill the last chunk, it
        will be dropped.
        """
        return type(self)(chunk(self, n))

    def chunk_default(self, n: int, default: T) -> "iter[typing.Tuple[T, ...]]":
        """Return an iterator containing the elements of this iterator in chunks
        of size n. If there are not enough elements to fill the last chunk, the
        missing elements will be replaced with the default value.
        """
        return type(self)(chunk_default(self, n, default))

    def _window(
        self, window_size: int
    ) -> typing.Generator[typing.Tuple[T, ...], None, None]:
        elements = deque()
        for _ in range(window_size):
            try:
                elements.append(self.next())
            except StopIteration:
                return

        yield tuple(elements)

        for el in self:
            elements.popleft()
            elements.append(el)
            yield tuple(elements)

    def window(self, window_size: int) -> "iter[typing.Tuple[T, ...]]":
        """Return an iterator containing the elements of this iterator in
        a sliding window of size window_size. If there are not enough elements
        to create a full window, the iterator will be empty.
        """
        return type(self)(self._window(window_size))

    def next(self) -> T:
        """Return the next element in the iterator, or raise StopIteration."""
        return next(self.it)

    def skip(self, n: int = 1) -> "iter[T]":
        """Skip and discard n elements from this iterator.

        Raises StopIteration if there are not enough elements.
        """
        for _ in builtins.range(n):
            self.next()
        return self

    def nth(self, n: int) -> T:
        """Return the nth element of this iterator.

        Discards all elements up to the nth element, and raises StopIteration
        if there are not enough elements.
        """
        self.skip(n)
        return self.next()

    def take(self, n: int) -> typing.Tuple[T, ...]:
        """Return the next n elements of this iterator.

        Raises StopIteration if there are not enough elements.
        """
        return tuple(self.next() for _ in builtins.range(n))

    def collect(self) -> "typing.List[T]":
        """Return a list containing all remaining elements of this iterator."""
        return list(self)

    def chain(self, other: typing.Iterable[T]) -> "iter[T]":
        """Return an iterator containing the elements of this iterator followed
        by the elements of other.
        """
        return type(self)(itertools.chain(self, other))

    @typing.overload
    def sum(self) -> T:
        ...

    @typing.overload
    def sum(self, initial: T) -> T:
        ...

    def sum(self, initial=_SENTINEL):
        """Return the sum of all elements in this iterator.

        If initial is provided, it is used as the initial value.
        """
        if initial is self._SENTINEL:
            return sum(self)
        return sum(self, initial)

    def sorted(
        self,
        key: typing.Union[typing.Callable[[T], U], None] = None,
        reverse: bool = False,
    ) -> "iter[T]":
        """Return an iterator containing the elements of this iterator sorted
        according to the given key and reverse parameters.
        """
        return type(self)(sorted(self, key=key, reverse=reverse))

    def reversed(self) -> "iter[T]":
        """Return an iterator containing the elements of this iterator in
        reverse order.
        """
        return type(self)(reversed(self))

    def min(self, key: typing.Union[typing.Callable[[T], U], None] = None) -> T:
        """Return the minimum element of this iterator, according to the given
        key.
        """
        return min(self, key=key)

    def max(self, key: typing.Union[typing.Callable[[T], U], None] = None) -> T:
        """Return the maximum element of this iterator, according to the given
        key.
        """
        return max(self, key=key)

    def tee(self, n: int = 2) -> typing.Tuple["iter[T]", ...]:
        """Return a tuple of n iterators containing the elements of this
        iterator.
        """
        return tuple(type(self)(iterator) for iterator in itertools.tee(self, n))

    def permutations(
        self, r: typing.Union[int, None] = None
    ) -> "iter[typing.Tuple[T, ...]]":
        """Return an iterator over the permutations of the elements of this
        iterator.

        If r is provided, the returned iterator will only contain permutations
        of size r.
        """
        return type(self)(itertools.permutations(self, r))

    def combinations(self, r: int) -> "iter[typing.Tuple[T, ...]]":
        """Return an iterator over the combinations, without replacement, of
        length r of the elements of this iterator.
        """
        return type(self)(itertools.combinations(self, r))

    def combinations_with_replacement(self, r: int) -> "iter[typing.Tuple[T, ...]]":
        """Return an iterator over the combinations, with replacement, of
        length r of the elements of this iterator.
        """
        return type(self)(itertools.combinations_with_replacement(self, r))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.it!r})"


@functools.wraps(range)
def range(*args, **kw):
    return iter(builtins.range(*args, **kw))
