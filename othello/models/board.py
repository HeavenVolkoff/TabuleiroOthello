# Internal
import typing as T
from itertools import product
from collections import Counter, defaultdict

# Project
from ..enums import Color
from .position import Position
from ..misc.line_view import LineView

# Type generics
BoardState_t = T.MutableMapping[T.Tuple[int, int], Color]


class Board:
    # Maintain compatibility with old version
    EMPTY, BLACK, WHITE, OUTER = Color  # type: ignore  # mypy issue #2305

    CORNERS = (Position(1, 1), Position(1, 8), Position(8, 1), Position(8, 8))

    # List of valid positions
    POSITIONS: T.Tuple[Position, ...] = tuple(
        Position(*pos) for pos in product(range(1, 9), repeat=2)
    )

    # Basic directions
    UP, DOWN, LEFT, RIGHT = Position(-1, 0), Position(1, 0), Position(0, -1), Position(0, 1)
    UP_RIGHT, DOWN_RIGHT, DOWN_LEFT, UP_LEFT = UP + RIGHT, DOWN + RIGHT, DOWN + LEFT, UP + LEFT
    DIRECTIONS = UP, UP_RIGHT, RIGHT, DOWN_RIGHT, DOWN, DOWN_LEFT, LEFT, UP_LEFT

    # According to: http://ceur-ws.org/Vol-1107/paper2.pdf
    MAX_TURNS = 60

    def __init__(self, board: T.Optional[BoardState_t]) -> None:
        self._turns = 0
        self._board: BoardState_t = defaultdict(lambda: Color.OUTER)

        if board is None:
            for i, j in self.POSITIONS:
                self[i, j] = Color.EMPTY

            self[4, 4], self[4, 5] = Color.WHITE, Color.BLACK
            self[5, 4], self[5, 5] = Color.BLACK, Color.WHITE
        else:
            self._board.update(board.items())

    def __iter__(self) -> T.Iterator[T.MutableSequence[Color]]:
        for i in range(0, 10):
            yield self[i]

    @T.overload
    def __getitem__(self, item: int) -> T.MutableSequence[Color]:
        ...

    @T.overload
    def __getitem__(self, item: T.Tuple[int, int]) -> Color:
        ...

    def __getitem__(
        self, item: T.Union[int, T.Tuple[int, int]]
    ) -> T.Union[T.MutableSequence[Color], Color]:
        if isinstance(item, int):
            return LineView(item, self._board)

        return self._board[item]

    def __setitem__(self, item: T.Tuple[int, int], value: T.Union[Color, str]) -> None:
        self._board[item] = Color(value)

    def play(self, move: T.Tuple[int, int], color: T.Union[Color, str]) -> "Board":
        assert color in (Color.BLACK, Color.WHITE)

        if move not in self.valid_moves(color):
            raise ValueError("Movimento inválido")

        self[move] = color

        for direction in Board.DIRECTIONS:
            self._make_flips(move, color, direction)

        self._turns += 1

        return self

    @property
    def board(self) -> "Board":
        # Maintain compatibility with old version
        return self

    @property
    def turns(self) -> int:
        return self._turns

    def score(self) -> T.Tuple[int, int]:
        score = Counter(
            self.board[pos] for pos in self.board.POSITIONS if self.board[pos] != Color.EMPTY
        )

        return score[Color.WHITE], score[Color.BLACK]

    def get_clone(self) -> "Board":
        return Board(self._board)

    def valid_moves(self, color: T.Union[Color, str]) -> T.Sequence[Position]:
        ret = []
        for i, j in self.POSITIONS:
            if self[i, j] == Color.EMPTY:
                for direction in Board.DIRECTIONS:
                    move = Position(i, j)
                    if self._find_bracket(move, color, direction):
                        ret.append(move)
        return tuple(ret)

    def get_square_color(self, l: int, c: int) -> Color:
        # Maintain compatibility with old version
        return self.board[l, c]

    def _make_flips(
        self, move: T.Tuple[int, int], color: T.Union[Color, str], direction: Position
    ) -> None:
        bracket = self._find_bracket(move, color, direction)

        if not bracket:
            return

        # flips
        square_pos = direction + move
        while square_pos != bracket:
            self[square_pos] = color
            square_pos += direction

    def _find_bracket(
        self, move: T.Tuple[int, int], color: T.Union[Color, str], direction: Position
    ) -> T.Optional[Position]:
        color = Color(color)
        bracket_pos = direction + move
        bracket_color = self[bracket_pos]

        if bracket_color == color:
            return None

        opponent = color.opposite()
        while bracket_color == opponent:
            bracket_pos += direction
            bracket_color = self[bracket_pos]

        return None if bracket_color in (Color.OUTER, Color.EMPTY) else bracket_pos


__all__ = ("Board",)
