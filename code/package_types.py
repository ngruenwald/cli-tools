# >> imports
from dataclasses import dataclass
# << imports

# >> types
@dataclass
class File:
    source: str
    target: str
    mode: str | None
    is_folder: bool


@dataclass
class Extract:
    strip: int
    prefix: str
    files: list[File]


@dataclass
class Package:
    name: str
    description: str
    alternatives: list[str]
    version: str
    version_pattern: str
    updated: str
    homepage: str
    package_url: str
    extract: Extract
    post_commands: list[str]
    package_file: str
# << types