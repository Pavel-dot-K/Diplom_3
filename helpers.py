import re


def _to_int_safe(txt: str) -> int:
    return int(re.sub(r"\D", "", txt or "") or 0)