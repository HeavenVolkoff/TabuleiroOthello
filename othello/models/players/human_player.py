# Internal
import typing as T

if T.TYPE_CHECKING:
    # Project
    from ...enums import Color
    from ...models import Board
    from ...abstract import AbstractView


class HumanPlayer:
    def __init__(self, color: "Color") -> None:
        self.color = color

    def play(self, board: "Board", view: "AbstractView") -> T.Tuple[int, int]:
        while True:
            model = view.Model(f"Próximo movimento do Jogador ({self.color.value})")
            model.add_input("Linha")
            model.add_input("Coluna")
            col_inp, row_inp = model.show(view)

            move = (int(row_inp), int(col_inp))

            if move in board.valid_moves(self.color):
                break

            view.alert("Movimento invalido. Insira um válido")

        return move


__all__ = ("HumanPlayer",)
