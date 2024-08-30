# >> imports
from subprocess import Popen
# << imports

# >> types
class Change:
    def __init__(self, file: str, name: str, old_version: str, new_version: str) -> None:
        self.file = file
        self.name = name
        self.old_version = old_version
        self.new_version = new_version
# << types

# >> create_commit_code
def create_commit(changes: list[Change]) -> bool:
    commands = []
    for change in changes:
        commands.append(["git", "add", change.file])
    if not commands:
        return True

    message = "maint: update packages\n"
    for change in changes:
        message += f"\n  * {change.name} {change.new_version}"
    commands.append(["git", "commit", "-m", message])

    for command in commands:
        proc = Popen(command)
        if proc.wait() != 0:
            return False

    return True
# << create_commit_code
