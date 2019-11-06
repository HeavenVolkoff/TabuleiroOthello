# Internal
import typing as T
from enum import Enum, unique


@unique
class Color(Enum):
    EMPTY = "."
    BLACK = "@"
    WHITE = "o"
    OUTER = "?"

    @classmethod
    def valid(cls) -> T.Tuple["Color", "Color"]:
        return cls.BLACK, cls.WHITE

    def __eq__(self, other: object) -> bool:
        ret: bool = self.value == other if isinstance(other, str) else super().__eq__(other)
        return ret

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        ret: int = self.value.__hash__()
        return ret

    def __repr__(self) -> str:
        return color_names[self]

    def opposite(self) -> "Color":
        if self in (Color.EMPTY, Color.OUTER):
            raise ValueError(f"Only {Color.BLACK} and {Color.WHITE} have opponents")

        return Color.BLACK if self is Color.WHITE else Color.WHITE


color_names = {
    Color.BLACK: "preto",
    Color.WHITE: "branco",
    Color.EMPTY: "vazio",
    Color.OUTER: "inválido",
}

__all__ = ("Color",)
