# Internal
import typing as T
from os import path
from glob import iglob
from inspect import isclass
from pkgutil import ModuleInfo
from itertools import chain
from importlib.util import module_from_spec
from importlib.machinery import FileFinder, SourceFileLoader

# Project
from ..abstract import PlayerProtocol
from ..models.board import Board


def available_players(player_paths: T.Optional[T.Sequence[str]] = None) -> T.Sequence[ModuleInfo]:
    import othello

    module_path: str = othello.__path__  # type: ignore  # mypy issue #1422
    player_paths = player_paths or tuple()
    return tuple(
        ModuleInfo(
            FileFinder(path.dirname(file_path), (SourceFileLoader, (".py",))),
            path.splitext(path.basename(file_path))[0],
            False,
        )
        for file_path in chain(
            *(
                iglob(path.join(dir_path, "**", "*.py"), recursive=True)
                for dir_path in chain(
                    (path.join(p, "models", "players") for p in module_path),
                    (dir_path for dir_path in player_paths if path.isdir(dir_path)),
                )
            ),
            (
                file_path
                for file_path in player_paths
                if path.isfile(file_path) and file_path.endswith(".py")
            ),
        )
        if not path.basename(file_path).startswith("_")
    )


def import_player(player_importer: ModuleInfo) -> T.Type[PlayerProtocol]:
    importer, module_name, _ = player_importer

    module_spec = importer.find_spec(module_name)
    if module_spec is None:
        raise ImportError(f"Failed to import player class from module: {module_name}")

    module = module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    module_all = getattr(module, "__all__", None)
    symbols = tuple(symbol for symbol in dir(module) if symbol[0] != "_")

    if module_all:
        symbols = tuple(symbol for symbol in symbols if symbol in module_all)

    objects = tuple(getattr(module, symbol) for symbol in symbols)

    try:
        player_cls: T.Type[PlayerProtocol] = next(
            cls
            for cls in objects
            if isclass(cls) and issubclass(cls, PlayerProtocol) and cls is not Board
        )
    except StopIteration:
        raise ImportError(f"Failed to import player class from module: {module_name}") from None

    return player_cls


__all__ = (
    "import_player",
    "available_players",
)
