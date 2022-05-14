import os
import yaml
import importlib_resources
from pathlib import Path


def fmt_proj(s: str):
    ix = s.rfind(".")
    if ix != -1:
        extension = s[ix:]
    else:
        extension = ""

    ns = s.replace(extension, "")
    ns = ns.replace(" ", "_")
    ns = ns.replace("-", "")
    ns = ns.lower()
    ns = ns.replace(".", "")

    ns = ns.replace("(", "")
    ns = ns.replace(")", "")

    if extension == ".png":
        ns = ns.replace("_at_", "_")
        ns = ns.replace("screen_shot_", "")

    return ns + extension


