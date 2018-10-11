#!/usr/bin/python

import argparse
import shutil
import os
import hashlib
import subprocess
import platform
import time

def silent_call(args, msg):
    os.system(args + "&> /dev/null")
    print(msg)

parser = argparse.ArgumentParser()
parser.add_argument("tex_file", help="The path to the main tex file to compile.")
parser.add_argument("--engine", help="The LaTeX engine to use; default is pdflatex.", default="/Library/TeX/texbin/pdflatex")
parser.add_argument("--bibengine", help="The bibliography engine to use; default is biber.", default="/Library/TeX/texbin/biber")
arguments = parser.parse_args()

source = arguments.tex_file
engine = arguments.engine
bibengine = arguments.bibengine

# Check to make sure the file exists.
if not os.path.exists(source):
    print("{} does not exist.".format(source))
    exit(1)

# Ensure that the source is an asbolute path.
source = os.path.abspath(source)
    
# Make sure it's not a directory.
if os.path.isdir(source):
    print("{} is a directory.".format(source))
    exit(1)
    
# Get some basic information about the file.
source_stub, source_extension = os.path.splitext(source.split("/")[source.count("/")])
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
silent_call("{} {}".format(engine, source_stub), "Finished LaTeX round 1.")
silent_call("{} {}".format(bibengine, source_stub), "Finished biber round 1.")
silent_call("{} {}".format(engine, source_stub), "Finished LaTeX round 2.")

# Check that a pdf was created.
pdf_name = source_stub + '.pdf'
pdf_path = os.path.join(destination, pdf_name)
final_pdf_path = os.path.join(source_directory, pdf_name)

if not os.path.exists(pdf_path):
    print("Failed to generate {}".format(pdf_name))
else:
    # Remove the pdf that will be rebuilt if it has already been built once.
    if os.path.exists(final_pdf_path):
        os.remove(final_pdf_path)
    shutil.move(pdf_path, final_pdf_path)

# Move back to our original directory.
os.chdir(source_directory)
    
# Make sure the pdf was moved back to the current directory.
if os.path.exists(final_pdf_path):
    print("Generated {}".format(pdf_name))
    if 'Darwin' in platform.system():
        subprocess.call(['open','-a','Preview',final_pdf_path])

