# Internal
import sys
import typing as T
import traceback
from os import environ
from argparse import ArgumentParser

# External
import typing_extensions as Te

# External
from othello.views import ConsoleView
from othello.abstract import AbstractView, AbstractTrainingView
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
    "--depurar",
    dest="debug",
    help="Habilita mostrar a stacktrace de errors e outros dados",
    action="store_true",
)
arg_parser.add_argument(
    "--treinamento",
    dest="training",
    help="Habilita modo de treinamento de um jogador",
    action="store_true",
)

debug = True


def main(view_type: str) -> None:
    global debug

    namespace = arg_parser.parse_args()
    debug = namespace.debug

    view = None
    training = namespace.training
    views_iter = iter(view for view in view_list[view_type] if view.available())
    while view is None:
        try:
            view_cls = next(views_iter)

            if training and not issubclass(view_cls, AbstractTrainingView):
                raise RuntimeError("Visualização não suporta mode de treino")

            view = view_cls(**vars(namespace))
        except StopIteration:
            break
        except Exception:
            if debug:
                traceback.print_exc()

            view = None
    else:
        try:
            return view.training_loop() if training else view.loop()
        except KeyboardInterrupt:
            print()
            pass

    raise RuntimeError("Unavailable view")


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
