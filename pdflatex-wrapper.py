#!/usr/bin/python

import argparse
import shutil
import os
import hashlib
import subprocess
import platform

parser = argparse.ArgumentParser()
parser.add_argument("tex_file", help="The path to the main tex file to compile.")
parser.add_argument("--engine", help="The LaTeX engine to use; default is pdflatex.", default="pdflatex")
parser.add_argument("--bibengine", help="The bibliography engine to use; default is biber.", default="biber")
arguments = parser.parse_args()

source = arguments.tex_file
engine = arguments.engine
bibengine = arguments.bibengine

# Check to make sure the file exists.
if not os.path.exists(source):
    print("{} does not exist.".format(source))
    exit(1)


# Make sure it's not a directory.
if os.path.isdir(source):
    print("{} is a directory.".format(source))
    exit(1)
    
# Get some basic information about the file.
source_stub, source_extension = os.path.splitext(source)
source_directory = os.path.dirname(source)

# Make sure it's a tex file.
if 'tex' not in source_extension:
    print("{} is not a .tex file.".format(source))


# Compute the destination by hashing the input file name.
sha256 = hashlib.sha256(source).hexdigest()
destination = "/tmp/pdf.latex.wrapper.cache/{}".format(sha256)

# Create the destination inode.
shutil.rmtree(destination, ignore_errors=True)
shutil.copytree(source_directory, destination)

# Change to the destination folder to compile.
os.chdir(destination)

# Compile
subprocess.call("{} {}".format(engine, source_stub), shell=True)
subprocess.call("{} {}".format(bibengine, source_stub), shell=True)
subprocess.call("{} {}".format(engine, source_stub), shell=True)

# Check that a pdf was created.
pdf_name = source_stub + '.pdf'
pdf_path = os.path.join(destination, pdf_name)

if not os.path.exists(pdf_path):
    print("Failed to generate {}".format(pdf_name))
else:
    shutil.move(pdf_path, source_directory)

# Move back to our original directory.
os.chdir(source_directory)
    
# Make sure the pdf was moved back to the current directory.
final_pdf_path = os.path.join(source_directory, pdf_name)

if os.path.exists(final_pdf_path):
    print("Generated {}".format(pdf_name))


# Open the pdf if on macOS.
if platform.system() == 'Darwin':
    subprocess.call('open {}'.format(final_pdf_path))
