# >> imports
import os
# << imports

# >> globals
TOKEN: str | None = None
# << globals

# >> set_token_code
def set_token(token: str | str) -> None:
    global TOKEN
    if not token:
        token = os.getenv("TOKEN")
    if not token:
        try:
            with open(".token", "r") as stream:
                lines = stream.readlines()
            for line in lines:
                k, v = line.split("=", maxsplit=1)
                if k == "TOKEN":
                    token = v
        except Exception:
            pass
    TOKEN = token


def get_token() -> None:
    global TOKEN
    return TOKEN
# << set_token_code
