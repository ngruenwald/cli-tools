# >> imports
import regex
# << imports

# >> update_package_code
def update_package(filepath: str, version: str, timestamp: str) -> None:
    try:
        rxv = regex.compile("^\\s*version\\s*=\\s*\".*\"\\s*$")
        rxu = regex.compile("^\\s*updated\\s*=\\s*\".*\"\\s*$")
        output: list[str] = []
        with open(filepath, "r") as stream:
            while True:
                line = stream.readline()
                if not line:
                    break
                m = rxv.match(line)
                if m:
                    line = f"version = \"{version}\"\n"
                m = rxu.match(line)
                if m:
                    line = f"updated = \"{timestamp}\"\n"
                output.append(line)
        with open(filepath, "w") as stream:
            stream.writelines(output)
    except Exception as error:
        print(f"failed to update {filepath}: {error}")
# << update_package_code
