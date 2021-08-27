#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Gustavo Romero Vazquez"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Gustavo Romero Vazquez"
__email__ = "gustavorv86@gmail.com"
__status__ = "Release"

import argparse
import glob
import os
import py_compile
import shutil
import sys
import uuid
import zipfile

PROGNAME = os.path.basename(sys.argv[0]).replace(".py", "")

DEFAULT_SHEBANG = "#!/usr/bin/env python3\n"


def mkzip(source_directory, zip_filename):
    fd_zip = zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED)

    for root, dirs, files in os.walk(source_directory):
        for filename in files:
            source_path = os.path.join(root, filename)
            destination_path = source_path.replace(source_directory, "")
            fd_zip.write(source_path, destination_path)

    fd_zip.close()


def mkbin(zip_filename, bin_filename):
    fdw = open(bin_filename, "wb")
    fdr = open(zip_filename, "rb")

    fdw.write(DEFAULT_SHEBANG.encode("utf-8"))
    while True:
        buffer_bytes = fdr.read(4096)
        if len(buffer_bytes) <= 0:
            break
        fdw.write(buffer_bytes)

    fdr.close()
    fdw.close()

    os.chmod(bin_filename, 0o750)


def build(main_filename: str, build_directory: str, bin_filename: str):
    shutil.rmtree(build_directory, ignore_errors=True)
    os.makedirs(build_directory, exist_ok=True)

    project_directory = os.path.dirname(main_filename)

    os.rename(main_filename, os.path.join(project_directory, "__main__.py"))

    py_filenames = [f for f in glob.glob(project_directory + "/**/*.py", recursive=True)]

    for py_filename in py_filenames:
        pyc_filename = py_filename.replace(project_directory, build_directory) + "c"
        py_compile.compile(py_filename, pyc_filename)

    os.rename(os.path.join(project_directory, "__main__.py"), main_filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Byte compile and binary application package Python 3 source files")
    parser.add_argument("-i", "--input", type=str, required=True, help="Main source file")
    parser.add_argument("-o", "--output", type=str, required=True, help="Output binary application package file")
    args = parser.parse_args()

    arg_input = args.input
    arg_output = args.output

    if not os.path.isfile(arg_input):
        print("ERROR: {} is not a file. Abort.".format(arg_input), file=sys.stderr)
        sys.exit(1)

    main_filename = os.path.abspath(arg_input)

    build_directory = os.path.dirname(arg_input) + ".build"
    build(main_filename, build_directory, arg_output)

    zip_filename = build_directory + ".zip"
    mkzip(build_directory, zip_filename)

    mkbin(zip_filename, arg_output)

    sys.exit(0)

