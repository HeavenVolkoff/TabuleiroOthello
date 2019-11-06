# Internal
import typing as T

# External
import typing_extensions as Te

if T.TYPE_CHECKING:
    # Project
    from ..enums import Color
    from ..models import Board


@Te.runtime
class PlayerProtocol(Te.Protocol):
    def __init__(self, __color: "Color"):
        ...

    def play(self, __board: "Board", **__kwargs: T.Any) -> T.Tuple[int, int]:
        ...


class ColoredPlayerProtocol(PlayerProtocol, Te.Protocol):
    color: "Color"

    def __init__(self, __color: "Color"):
        self.color = __color
