# Internal
import sys
import typing as T
from os import path
from inspect import isclass
from pkgutil import ModuleInfo, walk_packages
from importlib.util import module_from_spec
from importlib.machinery import FileFinder, SourceFileLoader

# Project
from ..models.board import Board

# Type generic
K = T.TypeVar("K", bound=type)


def available_players(player_paths: T.Optional[T.Sequence[str]] = None) -> T.Sequence[ModuleInfo]:
    import othello

    module_paths = set(player_paths) if player_paths else set()
    othello_path: str = othello.__path__  # type: ignore  # mypy issue #1422
    package_paths = {
        *(path.join(p, "models", "players") for p in othello_path),
        *(dir_path for dir_path in module_paths if path.isdir(dir_path)),
    }

    module_paths -= package_paths
    return (
        *walk_packages(package_paths),
        *(
            ModuleInfo(
                FileFinder(
                    path.dirname(module_path),
                    (SourceFileLoader, (".py",)),  # type: ignore # typeshed is incorrect
                ),
                path.splitext(path.basename(module_path))[0],
                False,
            )
            for module_path in module_paths
            if (
                path.isfile(module_path)
                and module_path.endswith(".py")
                and not path.basename(module_path).startswith("_")
            )
        ),
    )


def import_player(player_importer: ModuleInfo, protocol: K) -> K:
    loader, module_name, is_package = player_importer

    if is_package:
        sys.path.append(loader.path)

    module_spec = loader.find_spec(module_name)
    if module_spec is None:
        raise ImportError(
            f"Falha ao importar {'pacote' if is_package else 'modulo'} em "
            f"{path.join(loader.path, module_name)}"
        )

    module = module_from_spec(module_spec)
    module_spec.loader.exec_module(module)

    symbols = tuple(symbol for symbol in dir(module) if symbol[0] != "_")
    module_all = getattr(module, "__all__", None)
    if module_all:
        symbols = tuple(symbol for symbol in symbols if symbol in module_all)

    objects = tuple(getattr(module, symbol) for symbol in symbols)

    try:
        player_cls: K = next(
            cls
            for cls in objects
            if isclass(cls) and issubclass(cls, protocol) and cls is not Board
        )
    except StopIteration:
        raise ImportError(
            f"Nenhuma classe que implemente {protocol.__qualname__} foi "
            f"encontrada em {path.join(loader.path, module_name)}"
        ) from None

    return player_cls


__all__ = ("import_player", "available_players")
