# Internal
import sys
import typing as T
import traceback
from shutil import get_terminal_size

# Project
from ..enums import Color
from ..abstract import AbstractTrainingView, TrainingPlayerProtocol
from ..adapters import BoardAdapter, BoardTrainingAdapter
from ..misc.runtime_importer import available_players

if T.TYPE_CHECKING:
    # Internal
    from pkgutil import ModuleInfo


LOGO = """\
   _|_|      _|      _|                  _|  _|
 _|    _|  _|_|_|_|  _|_|_|      _|_|    _|  _|    _|_|
 _|    _|    _|      _|    _|  _|_|_|_|  _|  _|  _|    _|
 _|    _|    _|      _|    _|  _|        _|  _|  _|    _|
   _|_|        _|_|  _|    _|    _|_|_|  _|  _|    _|_|"""


class ConsoleView(AbstractTrainingView):
    ASK_MSG = "Selecione um dos players abaixo para ser o jogador"

    @staticmethod
    def print_view_data(adapter: BoardAdapter) -> None:
        print("┌─────────────────────┐")
        print("│     1 2 3 4 5 6 7 8 │")
        print("├───┬─────────────────┤")

        for i, column in enumerate(adapter.view_data):
            print(f"│ {i + 1} │ " + " ".join(v.value for v in column) + " │")

        print("└───┴─────────────────┘")

    class Model(AbstractTrainingView.Model["ConsoleView"]):
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
        print(LOGO)

        all_players = available_players(self.player_paths)
        adapter = BoardAdapter(
            self.ask_for_player(f"{self.ASK_MSG} {repr(Color.BLACK)}", all_players),
            self.ask_for_player(f"{self.ASK_MSG} {repr(Color.WHITE)}", all_players),
        )

        finished = False
        while not finished:
            if not self.automatic:
                input()

            color = adapter.current_color

            self.print_view_data(adapter)
            print(
                (
                    "Score: "
                    + " ".join(
                        f"{repr(color)} = {score}" for color, score in adapter.score.items()
                    )
                )
            )
            print(f"Rodada do jogador: {repr(color)} ({color.value})\n")

            try:
                update = adapter.update(self)
                finished = adapter.finished()
            except Exception as exc:
                if self.debug:
                    traceback.print_exc()
                else:
                    self.alert(f"ERROR: {exc}")

                break

            if not update:
                print(f"Sem movimentos para o jogador")

        print()

        self.print_view_data(adapter)
        print(
            (
                "Score: "
                + " ".join(f"{repr(color)} = {score}" for color, score in adapter.score.items())
            )
        )

        if adapter.failure:
            assert adapter.winner
            print(f"Jogador {repr(adapter.winner)} Ganhou por W/O")
        else:
            if adapter.winner:
                print(f"Jogador {repr(adapter.winner)} Ganhou")
            else:
                print("Empate")

    def training_loop(self) -> None:
        print(LOGO)
        print(" # Training Mode # ")

        all_players = available_players(self.player_paths)
        keep_running = True
        training_player: T.Union["ModuleInfo", "TrainingPlayerProtocol"] = self.ask_for_player(
            f"Selecione o jogador ({repr(Color.BLACK)}) para treino", all_players
        )
        competing_player = self.ask_for_player(f"{self.ASK_MSG} {repr(Color.WHITE)}", all_players)
        counter = {"game": 0, "round": 0}

        while keep_running:
            adapter = BoardTrainingAdapter(training_player, competing_player)
            counter["game"] += 1
            # Cache training player for consecutive games
            training_player = adapter.training_player

            while not adapter.finished:
                counter["round"] += 1

                self.update_line(f"Partida {counter['game']}, Rodada {counter['round']}")

                try:
                    update = adapter.update(self)
                except Exception as exc:
                    if self.debug:
                        traceback.print_exc()
                    else:
                        self.alert(f"ERROR: {exc}")

                    if not self.automatic:
                        answer = self.input("Continuar treino? (Y/n)") or "Y"
                        if answer not in ("y", "Y"):
                            keep_running = False

                    break

                if not update:
                    continue

    def ask_for_player(self, title: str, players: T.Sequence["ModuleInfo"]) -> "ModuleInfo":
        while True:
            print(title)

            for idx, player_info in enumerate(players):
                print(f"{idx} - {player_info.name}")

            try:
                chosen_pos = int(self.input("Digite o numero do player que voce deseja"))
            except ValueError:
                self.alert("Escolha deve ser um inteiro")
                continue

            if 0 <= chosen_pos < len(players):
                return players[chosen_pos]

            self.alert("Escolha inválida")

    def print(self, msg: str) -> None:
        print(msg)

    def alert(self, msg: str) -> None:
        print(msg, file=sys.stderr)

    def input(self, msg: str) -> str:
        return input(f"{msg}: ")

    def update_line(self, msg: str) -> None:
        terminal_size = get_terminal_size((80, 20))
        print("\r" + msg.ljust(terminal_size.columns), end="")


__all__ = ("ConsoleView",)
