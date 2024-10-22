# >> imports
from copy import deepcopy
# << imports

# >> resolve_vars_code
def resolve_vars(data: dict, vars: dict) -> dict:
    odata = deepcopy(data)
    fill_package_vars(odata, vars)  # TODO: modifies the input data!
    return odata


def fn_replace(input: str, frm: str, to: str) -> str:
    try:
        return input.replace(frm.strip("\"\'"), to.strip("\"\'"))
    except Exception:
        return input


def fn_cut(input: str, separator: str, index: str, count: str | None) -> str:
    try:
        sep = separator.strip("\"\'")
        idx = int(index.strip("\"\'"))
        parts = input.split(sep)
        if count:
            cnt = int(count.strip("\"\'"))
            return sep.join(parts[idx:cnt])
        return sep.join(parts[idx])
    except Exception:
        return input


def fill_package_vars(data: dict, extra_vars: dict):
    functions: dict[str, callable] = {
        "replace": fn_replace,
        "cut": fn_cut
    }

    def _get_val(data: dict, key: list[str]) -> str:
        if len(key) == 1:
            return str(data.get(key[0], ""))
        if key[0] not in data:
            return ""
        return _get_val(data[key[0]], key[1:])

    def _is_func(key: str) -> bool:
        try:
            if key[0] != '(':
                return False
            if key[-1] != ')':
                return False
            fname = key[1:-1].split(',')[0].strip()
            return fname in functions
        except Exception as err:
            print(f"error '_is_func': {err}")
        return False

    def _call_func(key: str, s: dict) -> str:
        try:
            parts = key.strip('()').split(",")  # TODO: do not split strings!
            parts = [p.strip() for p in parts]
            # fname = parts[0]
            # var = _get_val(s, parts[1].split("."))
            return functions[parts[0]](_get_val(s, parts[1].split(".")), *parts[2:])    # TODO: parts length!
        except Exception as err:
            print(f"error '_call_func': {err}")
        return ""

    def _find_beg_end(t: str) -> tuple[int, int]:
        beg = 0
        while True:
            beg = t.find("{{", beg)
            if beg == -1:
                return -1, -1
            end = t.find("}}", beg + 2)
            if end == -1:
                return -1, -1
            beg2 = t.find("{{", beg + 2)
            if beg2 == -1:
                return beg, end
            if beg2 > end:
                return beg, end
            beg = beg2

    def _fill_str_vars(t: str, s: dict) -> str:
        loop = True
        while loop:
            beg, end = _find_beg_end(t)
            if beg == -1:
                break
            old = t[beg:end+2]
            key = t[beg+2:end].strip()
            if _is_func(key):
                new = _call_func(key, s)
            else:
                new = _get_val(s, key.split("."))
            t = t.replace(old, new)
        return t

    def _fill_list_vars(t: list, s: dict):
        for i in range(len(t)):
            if isinstance(t[i], str):
                t[i] = _fill_str_vars(t[i], s)
            elif isinstance(t[i], list):
                _fill_list_vars(t[i], s)
            elif isinstance(t[i], dict):
                _fill_dict_vars(t[i], s)

    def _fill_dict_vars(t: dict, s: dict):
        for k, v in t.items():
            if isinstance(v, str):
                t[k] = _fill_str_vars(t[k], s)
            elif isinstance(v, list):
                _fill_list_vars(v, s)
            elif isinstance(v, dict):
                _fill_dict_vars(v, s)

    if "vars" not in data:
        data["vars"] = {}
    if "vars" in extra_vars:
        ev = extra_vars["vars"]
    else:
        ev = extra_vars
    for k, v in ev.items():
        if k not in data["vars"]:
            data["vars"][k] = v

    _fill_dict_vars(data, data)
# << resolve_vars_code
