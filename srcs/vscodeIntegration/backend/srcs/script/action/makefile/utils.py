from pathlib import Path

from srcs.script.MakefileConfigEntry.utils import readEntries
from srcs.script.action.makefile.Makefile import Makefile

CONFIG_REL_PATH = Path(".vscode/makefileConfig.json")


def buildMakefiles() -> list[Makefile]:
    config_path = (Path.cwd() / CONFIG_REL_PATH).resolve()
    if not config_path.exists():
        return []
    entries = readEntries(config_path)
    return [Makefile(entry) for entry in entries]


def getOutputMakefilePath(makefile: Makefile, workspace_root: Path | None = None) -> Path:
    if workspace_root is None:
        workspace_root = Path.cwd().resolve()
    return (workspace_root / makefile.output_makefile).resolve()
