"""run.py

Usage:
    run.py [options] [version]

Options:
    -c, --user-contrib     Compile for user contrib
"""

import docopt
import fitz
import os
import requests
import subprocess as sp
import json


URL = "https://github.com/pymupdf/PyMuPDF/archive/{version}.tar.gz"


COMMANDS = {
    "aria2c": ["aria2c", "--out=PyMuPDF.tar.gz"],
    "wget": ["wget", "--output-file=PyMuPDF.tar.gz"],
}


def main():
    args = docopt.docopt(__doc__)
    version = args["version"]
    if not version:
        version = fitz.version[0]

    command = COMMANDS["aria2c"] if sp.run(["which", "aria2c"]).returncode == 0 else COMMANDS["wget"]

    sp.run(["mkdir", "-p", "data"], check=True)
    os.chdir("data")
    sp.run([*command, URL.format(version=version)], check=True)
    sp.run(["tar", "-xf", "PyMuPDF.tar.gz"], check=True)
    sp.run(["sphinx-build", f"PyMuPDF-{version}/docs", "./PyMuPDF-docs"], check=True)
    sp.run(["convert", f"PyMuPDF-{version}/docs/pymupdf-logo.jpg", "pymupdf-logo.png"], check=True)
    sp.run(["doc2dash", "-n", "PyMuPDF", "-i", "pymupdf-logo.png", "-d", ".", "./PyMuPDF-docs"], check=True)

    if not args["--user-contrib"]:
        return

    sp.run(["mkdir", "-p", "user_contrib/PyMuPDF"], check=True)
    sp.run(["tar", "--exclude='.DS_Store'", "-cvzf", "user_contrib/PyMuPDF/PyMuPDF.tgz", "PyMuPDF.docset"], check=True)
    sp.run(["cp", "PyMuPDF.docset/icon.png", "user_contrib/PyMuPDF"], check=True)
    sp.run(["cp", "../README.md", "user_contrib/PyMuPDF"], check=True)
    sp.run(["touch", "user_contrib/PyMuPDF/docset.json"], check=True)
    with open("user_contrib/PyMuPDF/docset.json", "w") as file:
        data = {
            "name": "PyMuPDF",
            "version": version,
            "archive": "PyMuPDF.tgz",
            "author": {
                "name": "PowerSnail",
                "link": "https://github.com/PowerSnail"
            },
            "aliases": ["pymupdf"]
        }
        json.dump(data, file, indent=4)



if __name__ == "__main__":
    main()