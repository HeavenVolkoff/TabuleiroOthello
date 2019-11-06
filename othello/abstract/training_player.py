# Internal
import typing as T

# External
import typing_extensions as Te

# Project
from .player import PlayerProtocol

if T.TYPE_CHECKING:
    # Project
    from ..enums import Color
    from ..models.board import Board


@Te.runtime
class TrainingPlayerProtocol(PlayerProtocol, Te.Protocol):
    def game_over(self, __winner: T.Optional["Color"], __board: "Board") -> None:
        ...
