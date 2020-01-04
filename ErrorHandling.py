#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program: ContigExtractor
Description: This program can find ID corresponding to contigs from a input references in your MinION data.
Step 0: This is the error handling of the step "Get input"
Version: 1.0
Author: Catrine Ahrens Høm
"""

# Import libraries
import sys
import os
import gzip
from argparse import ArgumentParser

###########################################################################
# FUNCTIONS
###########################################################################

def CheckGZip(filename):
    """
    This function checks if the input file is gzipped.
    """
    gzipped_type = b"\x1f\x8b"

    infile = open(filename,"rb")
    filetype = infile.read(2)
    infile.close()
    if filetype is gzipped_type:
        return True
    else:
        return False

def OpenFile(filename,mode):
    """
    This function opens the input file in chosen mode.
    """
    try:
        if CheckGZip(filename):
            infile = gzip.open(filename,mode)
        else:
            infile = open(filename,mode)
    except IOError as error:
        sys.exit("Can't open file, reason: {} \n".format(error))
    return infile

def CheckFastq(filenames):
    """
    This function checks if all input files (list) are in fastq format.
    Outputs a list of True/False for each file.
    """
    fastq = list()
    fastq_type = b"@"

    # Open all files and get the first character
    for infile in filenames:
        f = OpenFile(infile, "rb")
        first_char = f.read(1);
        f.close()
        # Check if fastq
        if first_char is fastq_type:
            fastq.append(True)
        else:
            fastq.append(False)
    return fastq

def CheckFasta(filenames):
    """
    This function checks if all the input files (list) are in fasta format.
    Outputs a list of True/False for each file.
    """
    fasta = list()
    fasta_type = b">"

    # Open file and get the first character
    for infile in filenames:
        f = OpenFile(infile, "rb")
        first_char = f.read(1);
        f.close()
        # Check if fasta
        if first_char is fasta_type:
            fasta.append(True)
        else:
            fasta.append(False)
    return fasta

###########################################################################
# GET INPUT
###########################################################################

if __name__ == '__main__':
    # Parse input from command line
    parser = ArgumentParser()
    parser.add_argument("-i", dest="input_fastq", help="Fastq file", nargs = "+")
    parser.add_argument("-r", dest="r",help="References you want to map to", nargs = "+")
    parser.add_argument("-g", dest="g",help="Unicycler assembly.gfa file")
    parser.add_argument("-o", dest="o", help="Output filename")
    parser.add_argument("-f", dest="f",help="Unicycler assembly.fasta file")
    args = parser.parse_args()

    # Define input as variables
    input_fastq = args.input_fastq
    r = args.r
    o = args.o

    if args.g:
        g = args.g

    if args.f:
        f = args.f

# Open log file
logname = "{}/{}.log".format(o, o)
logfile = OpenFile(logname,"a+")

###########################################################################
# TEST INPUT
###########################################################################

# Test if fasta references and fastq files is exists in folder
for file in input_fastq:
    if os.path.exists(file) is False:
        logfile.write("Input Error: {} does not exist in path.".format(file))
        sys.exit("Input Error: {} does not exist in path.".format(file))

for file in r:
    if os.path.exists(file) is False:
        message = "Input Error: {} does not exist in path.".format(file)
        logfile.write(message)
        sys.exit(message)

# Test if references and input files is correct format
r_check_fasta = CheckFasta(r)

input_check_fasta = CheckFasta(input_fastq)
input_check_fastq = CheckFastq(input_fastq)

# References should be in fasta format
for i in range(0,len(r_check_fasta)):
    if r_check_fasta[i] is False:
        message = "Input Error: {} is a wrong format. Should be fasta format.".format(r[i])
        logfile.write(message)
        sys.exit(message)

# Input data should be fastq or fasta format
for i in range(0,len(input_check_fasta)):
    if input_check_fasta[i] is False and input_check_fastq[i] is False:
        message = "Input Error: {} is a wrong format. Should be fastq or fasta format.".format(input_fastq[i])
        logfile.write(message)
        sys.exit(message)

# Test Unicycler input if given
if args.g:
    if os.path.exists(g) is False:
        message = "Input Error: {} does not exist in path.".format(g)
        logfile.write(message)
        sys.exit(message)

    if os.path.exists(f) is False:
        message = "Input Error: {} does not exist in path.".format(f)
        logfile.write(message)
        sys.exit(message)


    ### Check that the input is gfa and fasta
    # Define variables
    fasta_type = ">"
    gfa_type = "S"

    # Open f file and get the first character
    file = open(f, "r")
    first_char = file.read(1);
    file.close()

    # Check if fasta
    if first_char is not fasta_type:
        message = "Error! Unknown format of input file: {}. Should be fasta format.".format(f)
        logfile.write(message)
        sys.exit(message)


    # Open g file and get the first character
    file = open(g, "r")
    first_char = file.read(1);
    file.close()

    # Check if gfa
    if first_char is not gfa_type:
        message = "Error! Unknown format of input file: {}. Should be gfa format".format(g)
        logfile(message)
        sys.exit(message)

# Close files
logfile.close()
