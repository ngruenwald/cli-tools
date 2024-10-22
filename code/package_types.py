# >> imports
from dataclasses import dataclass
# << imports

# >> types
@dataclass
class Repository:
    reponame: str
    repotype: str
    hostname: str
    basepath: str
    username: str | None
    password: str | None


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
class BuildScript:
    name: str
    content: list[str]


@dataclass
class BuildStep:
    name: str
    command: list[str]


@dataclass
class BuildPublish:
    repository_name: str
    repository_path: str
    files: list[str]


@dataclass
class Build:
    package_url: str
    query_url: str
    verify_ssl: bool
    version_pattern: str
    scripts: list[BuildScript]
    steps: list[BuildStep]
    publish: list[BuildPublish]


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
    query_url: str
    verify_ssl: bool
    extract: Extract
    post_commands: list[str]
    package_file: str
    build: Build | None
# << types