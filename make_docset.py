"""make_docset.py

Usage:
    make_docset.py [options] [version]

Options:
    -c, --user-contrib     Compile for user contrib
"""

import docopt
import fitz
import os
import subprocess as sp
import json
import sys


URL = "https://github.com/pymupdf/PyMuPDF/archive/{version}.tar.gz"


COMMANDS = {
    "aria2c": ["aria2c", "--out=PyMuPDF.tar.gz"],
    "wget": ["wget", "--output-file=PyMuPDF.tar.gz"],
    "curl": ["curl", "-L", "-o", "PyMuPDF.tar.gz"],
}


def main():
    args = docopt.docopt(__doc__)
    version = args["version"]
    if not version:
        version = fitz.version[0]

    if sp.run(["which", "aria2c"]).returncode == 0:
        command = COMMANDS["aria2c"]
    elif sp.run(["which", "wget"]).returncode == 0:
        command = COMMANDS["wget"]
    elif sp.run(["which", "curl"]).returncode == 0:
        command = COMMANDS["curl"]
    else:
        print("Error: unable to find download utility")
        print()
        print("Please make sure one of the following is installed and on your path:")
        for i in COMMANDS.keys():
            print("\t" + i)
        sys.exit(1)

    sp.run(["mkdir", "-p", "data"], check=True)
    os.chdir("data")
    sp.run([*command, URL.format(version=version)], check=True)
    sp.run(["tar", "-xf", "PyMuPDF.tar.gz"], check=True)
    sp.run(["sphinx-build", f"PyMuPDF-{version}/docs", "./PyMuPDF-docs"], check=True)
    sp.run(
        [
            "doc2dash",
            "-n",
            "PyMuPDF",
            "-i",
            f"PyMuPDF-{version}/docs/images/pymupdf-logo.png",
            "-d",
            ".",
            "./PyMuPDF-docs",
        ],
        check=True,
    )

    print("Docset is built: data/PyMuPDF.docset")

    if not args["--user-contrib"]:
        return

    sp.run(["mkdir", "-p", "user_contrib/PyMuPDF"], check=True)

    if sp.run(["which", "convert"]).returncode != 0:
        print("Error: unable to make icons")
        print("Please make sure ImageMagick is installed and on your path")
        sys.exit(1)
    # Making 32x32 and 64x64 icons
    sp.run(["convert", "PyMuPDF.docset/icon.png", "-resize", "16x16^", "-crop", "16x16+0+0", "user_contrib/PyMuPDF/icon.png"], check=True)
    sp.run(["convert", "PyMuPDF.docset/icon.png", "-resize", "32x32^", "-crop", "32x32+0+0", "user_contrib/PyMuPDF/icon@2x.png"], check=True)

    # Package docset
    sp.run(["tar", "--exclude='.DS_Store'", "-cvzf", "user_contrib/PyMuPDF/PyMuPDF.tgz", "PyMuPDF.docset"], check=True)
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

    print("Docset package for Dash-User-Contributions is built: data/user_contrib/PyMuPDF")



if __name__ == "__main__":
    main()
