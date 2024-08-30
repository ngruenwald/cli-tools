# >> ask_user_code
def ask_user(question: str) -> bool:
    while True:
        inp = input(f"{question} [Y/n] ").lower()
        if inp == "":
            return True
        if inp == "y":
            return True
        if inp == "n":
            return False
# << ask_user_code
