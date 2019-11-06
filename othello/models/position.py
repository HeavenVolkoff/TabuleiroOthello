# Internal
import typing as T

K = T.TypeVar("K", bound=T.Tuple[int, int])


class Position(T.NamedTuple):
    x: int
    y: int

    def __add__(self, other: T.Tuple[T.Any, ...]) -> "Position":
        return Position(self.x + other[0], self.y + other[1])

    def __iadd__(self, other: T.Tuple[T.Any, ...]) -> "Position":
        return self + other

    def __sub__(self, other: T.Tuple[T.Any, ...]) -> "Position":
        return Position(self.x - other[0], self.y - other[1])

    def __isub__(self, other: T.Tuple[T.Any, ...]) -> "Position":
        return self - other

    def __str__(self) -> str:
        return f"{self.x} {self.y}"


__all__ = ("Position",)
