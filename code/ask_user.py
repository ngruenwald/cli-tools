# >> imports
from enum import Enum
# << imports

# >> ask_user_code
class AskUserResult(Enum):
    YES = 1
    NO = 2
    ALL = 3

def ask_user(question: str, default: AskUserResult = AskUserResult.YES, include_all: bool = True) -> AskUserResult:
    text_yes: str = "Y" if default == AskUserResult.YES else "y"
    text_no: str = "N" if default == AskUserResult.NO else "n"
    text_all: str = "/a" if include_all else ""
    text_input: str = f"{question} [{text_yes}/{text_no}{text_all}] "
    while True:
        inp = input(text_input).lower()
        if inp == "":
            return default
        if inp == "y":
            return AskUserResult.YES
        if inp == "n":
            return AskUserResult.NO
        if include_all and inp == "a":
            return AskUserResult.ALL
# << ask_user_code
