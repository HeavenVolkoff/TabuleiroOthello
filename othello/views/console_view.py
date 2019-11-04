# Internal
import sys
import typing as T
import traceback

# Project
from ..enums import Color
from ..abstract import AbstractView, ColoredPlayerProtocol
from ..adapters import BoardAdapter
from ..misc.runtime_importer import import_player, available_players


class ConsoleView(AbstractView):
    @staticmethod
    def print_view_data(adapter: BoardAdapter) -> None:
        print("┌─────────────────────┐")
        print("│     1 2 3 4 5 6 7 8 │")
        print("├───┬─────────────────┤")

        for i, column in enumerate(adapter.view_data):
            print(f"│ {i + 1} │ " + " ".join(v.value for v in column) + " │")

        print("└───┴─────────────────┘")

    class Model(AbstractView.Model["ConsoleView"]):
        def show(self, view: "ConsoleView") -> T.Sequence[T.Optional[str]]:
            if self._title:
                print(self._title)

            result: T.List[T.Optional[str]] = []
            for name, data in self._structure:
                if name == "paragraph":
                    view.print(data["text"])
                    result.append(None)
                elif name == "input":
                    result.append(view.input(data["label"]))

            print("")

            return result

    @classmethod
    def available(cls) -> bool:
        return True

    def loop(self) -> None:
        print(
            """\
   _|_|      _|      _|                  _|  _|
 _|    _|  _|_|_|_|  _|_|_|      _|_|    _|  _|    _|_|
 _|    _|    _|      _|    _|  _|_|_|_|  _|  _|  _|    _|
 _|    _|    _|      _|    _|  _|        _|  _|  _|    _|
   _|_|        _|_|  _|    _|    _|_|_|  _|  _|    _|_|"""
        )

        colors = {Color.BLACK: "preto", Color.WHITE: "branco"}
        players: T.List["ColoredPlayerProtocol"] = []
        all_players = available_players(self.player_paths)
        for i, (color, name) in enumerate(colors.items()):
            while True:
                print(f"Selecione um dos players abaixo para ser o jogador {name}")

                for idx, player_info in enumerate(all_players):
                    print(f"{idx} - {player_info.name}")

                try:
                    chosen_pos = int(self.input("Digite o numero do player que voce deseja"))
                except ValueError:
                    self.alert("Escolha deve ser um inteiro")
                    continue

                if 0 <= chosen_pos < len(all_players):
                    break

                self.alert("Escolha inválida")

            player_cls: T.Type["ColoredPlayerProtocol"] = import_player(  # type: ignore
                all_players[chosen_pos]
            )

            player = player_cls(color)
            assert hasattr(player, "color")

            players.append(player)
            print()

        adapter = BoardAdapter(*players)
        walkover: T.Optional[Color] = None
        while not adapter.finished:
            if not self.automatic:
                input()

            color = adapter.current_color

            self.print_view_data(adapter)
            print(
                (
                    "Score: "
                    + " ".join(
                        f"{colors[color]} = {score}" for color, score in adapter.score.items()
                    )
                )
            )
            print(f"Rodada do jogador: {colors[color]} ({color.value})\n")

            try:
                update = adapter.update(self)
            except Exception as exc:
                walkover = color

                if self.debug:
                    traceback.print_exc()
                else:
                    self.alert(f"ERROR: {exc}")

                break

            if not update:
                print(f"Sem movimentos para o jogador")
                continue

        print()

        self.print_view_data(adapter)
        print(
            (
                "Score: "
                + " ".join(f"{colors[color]} = {score}" for color, score in adapter.score.items())
            )
        )

        if walkover:
            print(f"Jogador {colors[walkover.opposite()]} Ganhou por W/O")
        else:
            scores = adapter.score
            if scores[Color.WHITE] == scores[Color.BLACK]:
                print("Empate")
            else:
                print(
                    f"Jogador {colors[Color.BLACK] if scores[Color.BLACK] > scores[Color.WHITE] else colors[Color.WHITE]} Ganhou"
                )

    def print(self, msg: str) -> None:
        print(msg)

    def alert(self, msg: str) -> None:
        print(msg, file=sys.stderr)

    def input(self, msg: str) -> str:
        return input(f"{msg}: ")


__all__ = ("ConsoleView",)
