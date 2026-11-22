import tomllib
from pathlib import Path

from gf.core.output import GfError

DEFAULTS = Path(__file__).with_name("defaults.toml")


def load(project: Path) -> dict:
    config = tomllib.loads(DEFAULTS.read_text())
    override = project / ".gf" / "config.toml"
    if override.is_file():
        user = tomllib.loads(override.read_text())
        for section, values in user.items():
            config.setdefault(section, {}).update(values)
    return config


def model_for(project: Path, role: str) -> str:
    roles = load(project)["roles"]
    if role not in roles:
        raise GfError(f"역할 '{role}' 에 대한 모델이 설정에 없다. 가능한 역할: {', '.join(sorted(roles))}")
    return roles[role]
