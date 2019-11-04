# Internal
import sys
import typing as T
from os import environ
from argparse import ArgumentParser

# External
import typing_extensions as Te

# External
from othello.views import ConsoleView
from othello.abstract import AbstractView
from othello.misc.error_dialog import gui_error

view_list: T.Dict[str, T.Sequence[T.Type[AbstractView]]] = {
    "gui": tuple(),
    "console": (ConsoleView,),
}

arg_parser = ArgumentParser(description="Simula partidas do jogo Otello")
arg_parser.add_argument(
    "player_paths",
    type=str,
    help="Lista de caminhos para pastas ou arquivos contendo definições de jogadores em python",
    nargs="*",
    metavar="CAMINHO",
)
arg_parser.add_argument(
    "--automatico",
    dest="automatic",
    help="Passa para próxima jogada automaticamente",
    action="store_true",
)
arg_parser.add_argument(
    "--debug",
    dest="debug",
    help="Habilita mostrar a stacktrace de errors e outros dados ",
    action="store_true",
)

debug = True


def main(view_type: str) -> None:
    global debug

    namespace = arg_parser.parse_args()
    debug = namespace.debug

    try:
        view = next(view for view in view_list[view_type] if view.available())
    except StopIteration:
        raise RuntimeError("Unavailable view")

    try:
        view(**vars(namespace)).loop()
    except KeyboardInterrupt:
        print()
        pass


def error_msg(exc: BaseException) -> str:
    return f"Falha irrecuperável\nRazão: {exc}"


def main_gui() -> Te.NoReturn:
    try:
        main("gui")
    except BaseException as exc:
        gui_error(error_msg(exc))

        if debug:
            raise

        sys.exit(error_msg(exc))

    sys.exit(0)


def main_console() -> Te.NoReturn:
    try:
        main("console")
    except BaseException as exc:
        if debug:
            raise

        sys.exit(error_msg(exc))

    sys.exit(0)


if __name__ == "__main__":
    view_type = environ.get("OTHELLO_VIEW_TYPE", "console")

    try:
        main(view_type)
    except BaseException as exc:
        if view_type == "gui":
            gui_error(error_msg(exc))

        if debug:
            raise

        sys.exit(error_msg(exc))

    sys.exit(0)
