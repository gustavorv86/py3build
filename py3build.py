#!/usr/bin/env python3

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


def make_zip(source_directory, zip_filename):
	fd_zip = zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED)

	for root, dirs, files in os.walk(source_directory):
		for file in files:
			source_path = os.path.join(root, file)
			destination_path = source_path.replace(source_directory, "")
			fd_zip.write(source_path, destination_path)

	fd_zip.close()


def make_binary(zip_filename, bin_filename):
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


def build_from_python_project(project_directory: str, build_directory: str, bin_filename: str):
	os.makedirs(build_directory, exist_ok=True)

	main_filename = os.path.join(project_directory, "__main__.py")

	if not os.path.isfile(main_filename):
		print("ERROR: __main__.py file not found. Abort.".format(project_directory), file=sys.stderr)
		sys.exit(1)

	py_filenames = [f for f in glob.glob(project_directory + "/**/*.py", recursive=True)]

	for py_filename in py_filenames:
		pyc_filename = py_filename.replace(project_directory, build_directory) + "c"
		py_compile.compile(py_filename, pyc_filename)

	zip_filename = build_directory + "_pack.zip"
	make_zip(build_directory, zip_filename)

	make_binary(zip_filename, bin_filename)

	os.remove(zip_filename)
	shutil.rmtree(build_directory, ignore_errors=True)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Create a zipapp from Python 3 projects")
	parser.add_argument("-i", "--input", type=str, required=True, help="Python project directory with __main__.py application file")
	parser.add_argument("-o", "--output", type=str, required=True, help="Output zipapp executable file")
	args = parser.parse_args()

	arg_input = args.input
	arg_output = args.output
	
	if os.path.isdir(arg_output):
		progname_input = os.path.basename(arg_input)
		arg_output += "/" + progname_input
	
	build_directory = "/tmp/{}_{}".format(PROGNAME, uuid.uuid4().hex)

	if os.path.isdir(arg_input):
		project_directory = os.path.abspath(arg_input)
		build_from_python_project(project_directory, build_directory, arg_output)

	else:
		print("ERROR: invalid input {}. Abort.".format(arg_input), file=sys.stderr)
		sys.exit(1)
