import argparse

from package_types import Package
from set_token import get_token
from ask_user import ask_user
from create_commit import Change, create_commit, push_commit
from update_package import update_package

# >> imports
import re
import requests

from datetime import datetime, timezone
from functools import cmp_to_key
from time import sleep
# << imports

# >> globals
CHECK_SESSION: requests.Session | None = None
# << globals

# >> command_check_code
def create_command_check(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser("check", help="check for updates")
    parser.add_argument("--update", action="store_true", help="update package files")
    parser.add_argument("--yes", action="store_true", help="assume yes")
    parser.add_argument("--commit", action="store_true", help="commit changes")
    parser.add_argument("--push", action="store_true", help="push changes")
    parser.set_defaults(func=command_check)
    return parser


def command_check(packages: list[Package], args) -> int:

    class CheckPackageInfo:
        def __init__(self, host: str, owner: str, repo: str, version: str, pattern: str | None):
            self.host = host
            self.owner = owner
            self.repo = repo
            self.version = version
            self.pattern = pattern if pattern else r"^v?\d+\.\d+\.\d+$"

        @staticmethod
        def create(url: str, version: str, pattern: str | None) -> "CheckPackageInfo":
            from urllib.parse import urlparse
            m = urlparse(url)
            owner, repo = CheckPackageInfo.split_path(m.hostname, m.path)    # owner + repo = github specific?
            return CheckPackageInfo(m.hostname, owner, repo, version, pattern)

        @staticmethod
        def split_path(hostname: str, path: str) -> tuple[str, str]:
            # for now we only support github like urls, where the first part of the
            # path identifies the owner, and the second one the repository
            parts = path.split("/")
            if len(parts) == 1:
                return "", parts[0]     # no owner, just repo
            parts = [p for p in parts if p]
            return parts[0], parts[1]


    def get_session() -> requests.Session:
        global CHECK_SESSION
        if not CHECK_SESSION:
            CHECK_SESSION = requests.Session()
        return CHECK_SESSION


    def check_for_updates(pi: CheckPackageInfo) -> str|None:
        package = f"{pi.owner}/{pi.repo}"

        atags = api_get_list(f"https://api.github.com/repos/{package}/tags")
        tags = filter_tags(atags, pi.pattern)
        tags = sorted(tags, key=cmp_to_key(compare_tag_versions))

        if not tags:
            print(f"{pi.repo}: no tags!")
            return

        tag = tags[0]
        tag_version = trim_version_string(tag["name"])

        cmp_result = compare_versions(parse_version(pi.version), parse_version(tag_version))
        if cmp_result < 0:
            print(f"+ {pi.repo}: {pi.version} -> {tag_version}")
            return tag_version
        if cmp_result > 0:
            print(f"- {pi.repo}: {pi.version} != {tag_version}")
            return None
        return None


    def api_get_list(url: str) -> list:
        response = api_get(url)
        data = list(response.json())

        try:
            next_link = response.links["next"]["url"]
        except KeyError:
            next_link = None

        if next_link:
            sub_data = api_get_list(next_link)
            data.extend(sub_data)

        return data


    def api_get(url: str):
        token = get_token()
        num_loops = 10
        wait_seconds = 60
        for _ in range(0, num_loops):
            headers = { "Authorization": f"Bearer {token}" } if token else None
            response = get_session().get(url, headers=headers)
            if response.status_code == 403:
                # API rate limit?
                print("403 - waiting 60 seconds ...")
                sleep(wait_seconds)
            else:
                break
        response.raise_for_status()
        return response


    def filter_tags(tags: list, tag_filter: str) -> list:
        if not tag_filter:
            return tags
        return [t for t in tags if re.match(tag_filter, t.get("name", ""))]


    def trim_version_string(s: str) -> str:
        if not s:
            return s
        for idx in range(0, len(s)):
            if s[idx].isnumeric():
                break
        return s[idx:].strip()


    def compare_tag_versions(a: str, b: str) -> int:
        tag_a = parse_version(a["name"])
        tag_b = parse_version(b["name"])
        return compare_versions(tag_b, tag_a)


    def compare_versions(a, b) -> int:
        len_a = len(a)
        len_b = len(b)
        length = len_a if len_a < len_b else len_b
        for idx in range(0, length):
            if a[idx] == b[idx]:
                continue
            return a[idx] - b[idx]
        return 0


    def parse_version(s: str):
        def to_int(parts, idx) -> int:
            try:
                return int(parts[idx])
            except Exception:
                return 0

        delimiter = "."
        extra_delimiters = ["_", "-", "+"]
        s = trim_version_string(s)
        if len(s) > 0:
            for ed in extra_delimiters:
                s = s.replace(ed, delimiter)
        parts = s.split(delimiter)
        major = to_int(parts, 0)
        minor = to_int(parts, 1)
        patch = to_int(parts, 2)
        tweak = to_int(parts, 3)
        crazy = to_int(parts, 4)
        return (major, minor, patch, tweak, crazy)

    #
    #
    #

    if not get_token():
        print("WARN: no token - this will end badly")

    changes: list[Change] = []
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for package in packages:
        url = package.query_url
        ver = package.version if package.version else "0.0.0"
        pat = package.version_pattern
        pi = CheckPackageInfo.create(url, ver, pat)
        new_version = check_for_updates(pi)
        if args.update and new_version:
            changes.append(Change(package.package_file, package.name, package.version, new_version))

    changes_to_commit: list[Change] = []
    for change in changes:
        if args.yes:
            pass  # auto accept change
        elif ask_user(f"  update {change.name} from {change.old_version} to {change.new_version}?"):
            pass  # user accepted change
        else:
            continue
        update_package(change.file, change.new_version, timestamp)
        changes_to_commit.append(change)

    if args.commit and changes_to_commit:
        if create_commit(changes_to_commit):
            if args.push:
                push_commit()
# << command_check_code
