import argparse

from package_types import Package

# >> imports
from requests import get as requests_get

from os import system as os_system
from os import path as os_path, chmod
from os import makedirs

from io import BufferedReader
# << imports

# >> globals
GLOBAL_PREFIX=None
VERBOSE=False
# << globals

# >> command_install_code
def create_command_install(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser("install", help="install packages")
    parser.add_argument("-g", "--global-prefix", type=str)
    parser.add_argument("--no-post-commands", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument('packages', nargs=argparse.REMAINDER)
    parser.set_defaults(func=command_install)
    return parser


def command_install(packages: list[Package], args) -> int:

    def dry_run_package(package: Package) -> None:
        print(f"extract: strip={package.extract.strip}, prefix={package.extract.prefix}")
        for file in package.extract.files:
            print(f"source: {file.source}, target: {file.target}, mode: {file.mode}, is_folder: {file.is_folder}")


    def dry_run(packages: list[Package]) -> None:
        for package in packages:
            print(f"## {package.name} {package.version}")
            dry_run_package(package)
            print("")


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


    def extract_file_from_url(url: str) -> str:
        return os_path.basename(url)


    def extract_type_from_url(url: str) -> list[str]:
        try:
            parts = os_path.basename(url).split(".")
            if len(parts) == 1:
                return []
            ext = [parts[-1]]
            if len(parts) >= 2:
                if parts[-2] in ["tar"]:
                    ext.append(parts[-2])
            return ext
        except Exception:
            return ""


    def strip_path_parts(pp: list[str], strip: int) -> list[str] | None:
        if strip > len(pp):
            return None  # stripped
        if strip > 0:
            pp = pp[strip:]
        return pp


    def split_path_parts(path: str) -> list[str]:
        return path.replace("\\", "/").split("/")


    def join_path_parts(pp: list[str]) -> str:
        return "/".join(pp).replace("//", "/")


    def strip_file_path(path: str, strip: int) -> str | None:
        return join_path_parts(strip_path_parts(split_path_parts(path), strip))


    def get_file_path(pkg: Package, opath: str) -> str | None:
        pp = strip_path_parts(split_path_parts(opath), pkg.extract.strip)
        if not pp:
            return None
        if pkg.extract.prefix:
            pp.insert(0, pkg.extract.prefix)
        return join_path_parts(pp)


    def get_output_path(pkg: Package, opath: str) -> tuple[str | None, int | None]:
        if not pkg.extract.files:
            return get_file_path(pkg, opath), None
        pp = strip_path_parts(split_path_parts(opath), pkg.extract.strip)
        if not pp:
            return None, None
        sp = join_path_parts(pp)
        for pkgf in pkg.extract.files:
            if pkgf.is_folder:
                if sp.startswith(pkgf.source):
                    sub = sp[len(pkgf.source):]
                    if sub.startswith("/"):
                        sub = sub[1:]
                    res = os_path.join(pkgf.target, sub)
                    return res, pkgf.mode
            else:
                if sp == pkgf.source:
                    return pkgf.target, pkgf.mode
        return None, None


    def is_zip_type(type: list | str | None) -> bool:
        if not type:
            return False
        if isinstance(type, str):
            return type == "zip"
        return type[-1] == "zip"


    def is_tar_type(type: list | str | None) -> bool:
        if not type:
            return False
        if "tar" in type:
            return True
        if "tgz" in type:
            return True
        if "txz" in type:
            return True
        return False


    def extract_archive(pkg: Package, content: bytes) -> None:
        type = extract_type_from_url(pkg.package_url)
        if not type:  # no archive
            extract_none(pkg, content)
        elif is_zip_type(type):
            extract_zip(pkg, content)
        elif is_tar_type(type):
            extract_tar(pkg, content)
        else:
            extract_none(pkg, content)


    def make_path(p: str) -> None:
        basepath = os_path.dirname(p)
        if not basepath:
            return
        # todo test if root
        if basepath:
            makedirs(basepath, exist_ok=True)


    def write_file(path: str, content: bytes | BufferedReader | None, mode: int | None = None, create_path: bool = True) -> None:
        if create_path:
            make_path(path)

        if content is None:
            return

        with open(path, "wb") as stream:
            if isinstance(content, BufferedReader):
                while True:
                    tmp = content.read(64 * 1024)
                    if not tmp:
                        break
                    stream.write(tmp)
            else:
                stream.write(content)

        if mode is not None:
            if isinstance(mode, str):
                mode = int(mode, 8)
            chmod(path, mode)


    def extract_none(pkg: Package, content: bytes) -> None:
        fname = extract_file_from_url(pkg.package_url)
        fpath, fmode = get_output_path(pkg, fname)
        if fpath and GLOBAL_PREFIX:
            fpath = f"{GLOBAL_PREFIX}/{fpath}".replace("//", "/")
        if VERBOSE:
            print(f"{fname} -> {fpath if fpath else 'SKIP'}")
        if fpath:
            write_file(fpath, content, mode=fmode if fmode else 755, create_path=True)


    def extract_tar(pkg: Package, content: bytes) -> None:
        import io
        import tarfile
        with tarfile.open(fileobj=io.BytesIO(content), mode="r") as tf:
            for item in tf:
                fpath, fmode = get_output_path(pkg, item.path)
                if fpath and GLOBAL_PREFIX:
                    fpath = f"{GLOBAL_PREFIX}/{fpath}".replace("//", "/")
                if VERBOSE:
                    print(f"{item.path} -> {fpath if fpath else 'SKIP'}")
                if fpath:
                    write_file(fpath, tf.extractfile(item), mode=fmode if fmode else item.mode, create_path=True)


    def extract_zip(pkg: Package, content: bytes) -> None:
        import io
        import zipfile
        with zipfile.ZipFile(file=io.BytesIO(content), mode="r") as zf:
            for item in zf.filelist:
                fpath, fmode = get_output_path(pkg, item.filename)
                if fpath and GLOBAL_PREFIX:
                    fpath = f"{GLOBAL_PREFIX}/{fpath}".replace("//", "/")
                if VERBOSE:
                    print(f"{item.filename} -> {fpath if fpath else 'SKIP'}")
                if fpath:
                    write_file(fpath, zf.read(item), mode=fmode if fmode else 755, create_path=True)


    def download_file(url):
        rsp = requests_get(url, allow_redirects=True, verify=False)
        rsp.raise_for_status()
        return rsp.content


    def run_post_commands(commands):
        for command in commands:
            if VERBOSE:
                print(f"run_post_command:  {command}")
            os_system(command)


    def install_package(package: Package, no_post_commands: bool) -> None:
        print(f"* {package.name} {package.version}")
        content = download_file(package.package_url)
        extract_archive(package, content)
        if not no_post_commands:
            run_post_commands(package.post_commands)

    #
    #
    #

    packages = filter_packages(packages, args.packages)
    if not packages:
        raise Exception(f"package name required")

    if args.dry_run:
        dry_run(packages)
        return 0

    for package in packages:
        install_package(package, args.no_post_commands)
# << command_install_code
