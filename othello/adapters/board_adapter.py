# Internal
import typing as T
from inspect import signature

# Project
from ..enums import Color
from ..models import Board
from ..abstract import AbstractView, PlayerProtocol, ColoredPlayerProtocol
from ..misc.runtime_importer import import_player

if T.TYPE_CHECKING:
    # Internal
    from pkgutil import ModuleInfo


class Players(T.NamedTuple):
    black: ColoredPlayerProtocol
    white: ColoredPlayerProtocol

    def get_player(self, color: Color) -> ColoredPlayerProtocol:
        return self.black if color is color.BLACK else self.white


class BoardAdapter:
    def __init__(
        self,
        black: T.Union["ModuleInfo", PlayerProtocol],
        white: T.Union["ModuleInfo", PlayerProtocol],
    ) -> None:
        black_player = (
            black
            if isinstance(black, PlayerProtocol)
            else import_player(black, PlayerProtocol)(Color.BLACK)
        )
        white_player = (
            white
            if isinstance(white, PlayerProtocol)
            else import_player(white, PlayerProtocol)(Color.WHITE)
        )

        # Validate players
        assert hasattr(black_player, "color") and hasattr(white_player, "color")

        # Internal
        self._board = Board(None)
        self._failure: T.Optional[Color] = None
        self._players = Players(
            T.cast(ColoredPlayerProtocol, black_player),
            T.cast(ColoredPlayerProtocol, white_player),
        )
        self._current_player = self._players.black

    @property
    def score(self) -> T.Mapping[Color, int]:
        return dict(zip((Color.WHITE, Color.BLACK), self._board.score()))

    @property
    def winner(self) -> T.Optional[Color]:
        return (
            self._failure.opposite()
            if self._failure
            else (
                max(self.score, key=self.score.get)
                if self.score[Color.WHITE] != self.score[Color.BLACK]
                else None
            )
        )

    @property
    def failure(self) -> bool:
        return self._failure is not None

    @property
    def view_data(self) -> T.Sequence[T.Sequence[Color]]:
        return tuple(column[1:9] for column in self._board)[1:9]

    def finished(self) -> bool:
        return self._failure is not None or not (
            self._has_moves(Color.WHITE) or self._has_moves(Color.BLACK)
        )

    @property
    def current_color(self) -> Color:
        return self._current_player.color

    def update(self, view: AbstractView) -> bool:
        updated = False

        if self._has_moves(self._current_player.color):
            try:
                self._board.play(
                    self._current_player_generic_play(self._board.get_clone(), view),
                    self._current_player.color,
                )
            except Exception:
                self._failure = self._current_player.color
                raise

            updated = True

        self._current_player = self._players.get_player(self._current_player.color.opposite())

        return updated

    def _has_moves(self, color: Color) -> bool:
        return len(self._board.valid_moves(color)) > 0

    def _current_player_generic_play(self, board: Board, view: AbstractView) -> T.Tuple[int, int]:
        args_list = list(signature(self._current_player.play).parameters.keys())
        if args_list[0] in ("self", "cls"):
            args_list.pop(0)

        args = set(args_list) - {"kwargs"}
        if args == {"board"}:
            return self._current_player.play(board)
        else:
            return self._current_player.play(board, view=view)


__all__ = ("BoardAdapter",)
