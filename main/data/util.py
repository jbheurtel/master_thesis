import zipfile
import os


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


def zipfolder(source, dest):
    zipobj = zipfile.ZipFile(source + '.zip', 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(dest) + 1
    for base, dirs, files in os.walk(dest):
        for file in files:
            fn = os.path.join(base, file)
            zipobj.write(fn, fn[rootlen:])
