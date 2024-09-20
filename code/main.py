
# >> imports
import argparse
import sys
# << imports

from command_build import create_command_build
from command_check import create_command_check
from command_create import create_command_create
from command_install import create_command_install
from load_data import load_packages, load_vars
from package_types import Package
from set_token import set_token

# >> main_code
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--include", default=[], nargs="+")
    parser.add_argument("-e", "--exclude", default=[], nargs="+")
    parser.add_argument("-p", "--path", default="packages")
    parser.add_argument("-v", "--vars", default="vars.toml")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--token", type=str)

    subparsers = parser.add_subparsers(dest="subcommand", help='sub-command help')

    create_command_check(subparsers)
    create_command_install(subparsers)
    create_command_build(subparsers)
    create_command_create(subparsers)

    args = parser.parse_args()

    if args.subcommand is None:
        parser.print_help()
        return 1

    vars: dict[str, str] = load_vars(args.vars)
    packages: list[Package] = load_packages(args.path, vars, args.include, args.exclude)

    set_token(args.token)

    return args.func(packages, args)
# << main_code

# >> entrypoint
def disable_warnings():
    import urllib3
    urllib3.disable_warnings()


if __name__ == "__main__":
    try:
        disable_warnings()
        sys.exit(main())
    except Exception as err:
        print(err)
        sys.exit(1)
# << entrypoint
