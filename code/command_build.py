import argparse

from command_install import command_install
from load_data import load_repositories
from package_types import Repository, Package, BuildStep, BuildPublish

# >> imports
import logging
import os
import shutil
import tempfile

from requests import get as requests_get
from subprocess import Popen
# << imports

# >> globals
TEMP_PREFIX=None
# << globals

# >> command_build_code
def create_command_build(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser("build", help="build packages")
    parser.add_argument("--install", action="store_true", help="install after build")
    parser.add_argument("--no-publish", action="store_true", help="skip publish steps")
    parser.add_argument("--temp-prefix", type=str, help="prefix for temporary directories")
    parser.add_argument('packages', nargs=argparse.REMAINDER)
    parser.set_defaults(func=command_build)
    return parser


def command_build(packages: list[Package], args) -> int:

    def filter_packages(packages: list[Package], package_names: list[str]) -> list[Package]:
        results: list[Package] = []
        for package_name in package_names:
            found = False
            for package in packages:
                if package.name == package_name:
                    results.append(package)
                    found = True
                    break
            if not found:
                raise Exception(f"unknown package '{package_name}'")
        return results

    def download_source_package(sourceurl: str, targetpath: str, verify_ssl: bool) -> bool:
        try:
            rsp = requests_get(sourceurl, allow_redirects=True, verify=verify_ssl)
            rsp.raise_for_status()
            filename = sourceurl[sourceurl.rindex("/")+1:]
            filepath = os.path.join(targetpath, filename)
            with open(filepath, "wb") as f:
                f.write(rsp.content)
            return True
        except Exception as error:
            logging.error(error)
            return False

    def create_build_script(filepath: str, filecontent: list[str] | str) -> bool:
        try:
            with open(filepath, "wt") as f:
                if isinstance(filecontent, list):
                    f.write("\n".join(filecontent))
                else:
                    f.write(filecontent)
            return True
        except Exception as error:
            logging.error(error)
            return False

    def execute_build_step(step: BuildStep, workdir: str) -> bool:
        try:
            def filter(x: str) -> str:
                return x.replace("$PWD", workdir)

            command = [filter(x) for x in step.command]
            logging.debug(f"executing command: {command}")
            proc = Popen(command, cwd=workdir)
            return proc.wait() == 0
        except Exception as error:
            logging.error(error)
            return False

    def build_from_source(package: Package, workdir: str) -> bool:
        if not package.build:
            return
        for idx, script in enumerate(package.build.scripts):
            if not create_build_script(os.path.join(workdir, script.name), script.content):
                logging.error(f"could not create build script #{idx} '{script.name}'")
                return False
        for idx, step in enumerate(package.build.steps):
            if not execute_build_step(step, workdir):
                logging.error(f"build step #{idx} ('{step.name}') failed")
                return False
        return True

    def build_package(package: Package, workdir: str) -> bool:
        print(f"building {package.name} {package.version}")
        if not download_source_package(package.build.package_url, workdir, package.build.verify_ssl):
            return False
        if not build_from_source(package, workdir):
            return False
        return True

    def publish_package_folder(package: Package, publish: BuildPublish, repository: Repository, workdir: str) -> bool:
        for idx, file in enumerate(publish.files):
            try:
                src = os.path.join(workdir, file)
                dst = os.path.join(repository.basepath, publish.repository_path)  # TBD: append file?
                os.makedirs(dst, exist_ok=True)
                shutil.copy2(src, dst)
            except Exception as error:
                logging.error(f"could not publish file #{idx} '{file}': {error}")
                return False
        return True

    def publish_package(package: Package, repositories: list[Repository], workdir: str) -> bool:
        if not package.build:
            return True
        for idx, publish in enumerate(package.build.publish):
            repository: Repository = next(filter(lambda x: x.reponame == publish.repository_name, repositories), None)
            if not repository:
                logging.error(f"repository '{publish.repository_name}' not found")
                return False
            if repository.repotype == "folder":
                if not publish_package_folder(package, publish, repository, workdir):
                    return False
            else:
                logging.error(f"repository '{repository.reponame}': unsupported type '{repository.type}'")
                return False
        return True

    #
    #
    #

    repositories: list[Repository] = load_repositories(args.vars)

    packages = filter_packages(packages, args.packages)
    if not packages:
        raise Exception("package name required")

    for package in packages:
        if not package.build:
            logging.warning(f"package {package.name} has no build config")
            continue
        with tempfile.TemporaryDirectory() as workdir:
            try:
                if not build_package(package, workdir):
                    raise Exception("build failed")
                if not args.no_publish:
                    if not publish_package(package, repositories, workdir):
                        raise Exception("publish failed")
                if args.install:
                    if command_install(package, args) != 0:  # TODO: this won't work
                        raise Exception("install failed")
            except Exception as error:
                logging.error(error)
# << command_build_code
