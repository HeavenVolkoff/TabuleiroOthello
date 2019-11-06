# Internal
import typing as T

# Project
from ..enums import Color
from ..abstract import PlayerProtocol, TrainingPlayerProtocol
from .board_adapter import BoardAdapter
from ..misc.runtime_importer import import_player

if T.TYPE_CHECKING:
    # Internal
    from pkgutil import ModuleInfo


class BoardTrainingAdapter(BoardAdapter):
    def __init__(
        self,
        black: T.Union["ModuleInfo", TrainingPlayerProtocol],
        white: T.Union["ModuleInfo", PlayerProtocol],
    ) -> None:
        training_player = (
            black
            if isinstance(black, TrainingPlayerProtocol)
            else import_player(black, TrainingPlayerProtocol)(Color.BLACK)
        )

        super().__init__(training_player, white)

        self.training_player = training_player

    def finished(self) -> bool:
        is_finished = super().finished()
        if is_finished:
            self.training_player.game_over(self.winner, self._board)

        return is_finished
