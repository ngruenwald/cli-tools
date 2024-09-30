from package_types import (
    Build,
    BuildPublish,
    BuildScript,
    BuildStep,
    Extract,
    File,
    Package,
    Repository,
)
from resolve_vars import resolve_vars

# >> imports
import glob
import tomllib
# << imports

# >> load_packages_code
def load_vars(filepath: str) -> dict[str, str]:
    with open(filepath, "rb") as stream:
        return tomllib.load(stream)


def load_repositories(filepath: str) -> list[Repository]:
    def load_repository(data: dict) -> Repository:
        reponame: str = data.get("name", "")
        repotype: str = data.get("type", "folder")
        hostname: str = data.get("host", "")
        basepath: str = data.get("path", "")
        username: str | None = data.get("user", None)
        password: str | None = data.get("pass", None)
        return Repository(reponame, repotype, hostname, basepath, username, password)

    with open(filepath, "rb") as stream:
        data = tomllib.load(stream)
    return [load_repository(r) for r in data.get("repository")]


def load_package(filepath: str, data: dict) -> Package:
    def load_package_file(data: dict) -> File:
        source: str = data.get("source", "")
        target: str = data.get("target", "")
        mode: str | None = data.get("mode", None)
        is_folder: bool = data.get("is-folder", False)
        if not source:
            raise Exception("file has no source")
        if not target:
            raise Exception("file has no target")
        return File(source, target, mode, is_folder)

    def load_package_extract(data: dict) -> Extract:
        strip: int = data.get("strip", 0)
        prefix: str = data.get("prefix", "")
        files: list[File] = [load_package_file(df) for df in data.get("files", [])]
        return Extract(strip, prefix, files)

    def load_package_build_script(data: dict) -> BuildScript:
        name: str = data.get("name", "")
        if not name:
            raise Exception("build script name is missing or empty")
        content: list[str] = data.get("content", [])
        return BuildScript(name, content)

    def load_package_build_step(data: dict) -> BuildStep:
        name: str = data.get("name", "")
        command: list[str] = data.get("command", [])
        return BuildStep(name, command)

    def load_package_build_publish(data: dict) -> BuildPublish:
        repository_name: str = data.get("repository-name", "")  # TBD: exception if empty
        repository_path: str = data.get("repository-path", "")
        files: list[str] = data.get("files", [])
        return BuildPublish(repository_name, repository_path, files)

    def load_package_build(data: dict | None) -> Build | None:
        if not data:
            return None
        package_url = data.get("package-url", None)
        if package_url is None:
            raise Exception("build package-url is missing")
        verify_ssl: bool = data.get("verify-ssl", True)
        version_pattern: str = data.get("version-pattern", "")
        scripts: list[BuildScript] = [load_package_build_script(bs) for bs in data.get("script", [])]
        steps: list[BuildStep] = [load_package_build_step(bs) for bs in data.get("step", [])]
        publish: list[BuildPublish] = [load_package_build_publish(bp) for bp in data.get("publish", [])]
        return Build(package_url, verify_ssl, version_pattern, scripts, steps, publish)

    try:
        name: str = data.get("name", "")
        if not name:
            raise Exception("name is missing")
        version: str = data.get("version", None)
        if version is None:
            raise Exception("version is missing")
        package_url = data.get("package-url", None)
        if package_url is None:
            raise Exception("package-url is missing")
        verify_ssl: bool = data.get("verify-ssl", True)
        description: str = data.get("description", "")
        alternatives: list[str] = data.get("alternatives", [])
        updated: str = data.get("updated", "")
        homepage: str = data.get("homepage", "")
        version_pattern: str = data.get("version-pattern", "")
        extract = load_package_extract(data.get("extract", {}))
        post_commands: list[str] = data.get("post-commands", [])
        build: Build | None = load_package_build(data.get("build", None))
        return Package(
            name,
            description,
            alternatives,
            version,
            version_pattern,
            updated,
            homepage,
            package_url,
            verify_ssl,
            extract,
            post_commands,
            filepath,
            build
        )
    except Exception as err:
        raise Exception(f"package '{name}': {err}")


def load_package_from_file(filepath: str, vars: dict | None) -> Package | None:
    with open(filepath, "rb") as stream:
        data = tomllib.load(stream)
        data = resolve_vars(data, vars)
        return load_package(filepath, data)


def load_packages(path: str, vars: dict | None = None, include: list[str] | None = None, exclude: list[str] | None = None) -> list[Package]:
    packages: list[Package] = []
    for filepath in glob.glob(f"{path}/*.toml"):
        if include and not any(filepath.endswith(x) for x in include):
            continue
        if exclude and any(filepath.endswith(x) for x in exclude):
            continue
        packages.append(load_package_from_file(filepath, vars))
    return packages
# << load_packages_code
