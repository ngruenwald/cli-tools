import argparse

from package_types import Package

# >> imports
from datetime import datetime, timezone
from io import BufferedWriter
# << imports

# >> command_create_code
def create_command_create(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser("create", help="create files")
    parser.add_argument("--type", type=str, default="readme")
    parser.add_argument("file", type=str)
    parser.set_defaults(func=command_create)
    return parser


def command_create(packages: list[Package], args) -> int:

    def create_table_entry(package: Package) -> str:
        package_name = f"[{package.name}]({package.homepage})" if package.homepage else package.name
        package_alternatives = ", ".join(package.alternatives)
        # | Name | Description | Version | Updated | Alternatives |
        return f"| {package_name} | {package.description} | {package.version} | {package.updated} | {package_alternatives} |"


    def write_table(stream: BufferedWriter, packages: list[Package]) -> None:
        stream.write("| Name | Description | Version | Updated | Alternatives |\n")
        stream.write("|----- |------------ |-------- |-------- |------------- |\n")
        packages.sort(key=lambda package: package.name)
        for package in packages:
            stream.write(f"{create_table_entry(package)}\n")


    def create_readme(filepath: str, packages: list[Package]) -> None:
        with open(filepath, "w") as stream:
            stream.write("# Packages\n\n")
            write_table(stream, packages)
            stream.write(f"\n_last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} (utc)_\n")

    #
    #
    #

    if args.type == "readme":
        create_readme(args.file, packages)
        return 0

    print(f"unsupported type '{args.type}'")
    return 1
# << command_create_code
