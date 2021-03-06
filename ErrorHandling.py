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
    if filetype == gzipped_type:
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
        if first_char == fastq_type:
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
        if first_char == fasta_type:
            fasta.append(True)
        else:
            fasta.append(False)
    return fasta

def Checkgfa(filenames):
    """
    This function checks if all the input files (list) are in gfa format.
    Outputs a list of True/False for each file.
    """
    gfa = list()
    gfa_type = b"S"

    # Open file and get the first character
    for infile in filenames:
        f = OpenFile(infile, "rb")
        first_char = f.read(1);
        f.close()
        # Check if fasta
        if first_char == gfa_type:
            gfa.append(True)
        else:
            gfa.append(False)
    return gfa

def str2bool(c):
    if isinstance(c, bool):
       return c
    if c.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif c.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        message="Boolean value expected for c flag ('-c True' or '-c False'), but recieved: {}".format(c)
        logfile.write(message)
        sys.exit(message)

def str2int(l):
    try:
        l = int(l)
        return l
    except:
       message="Integer value expected for l flag, but recieved: {}, which is {}".format(l,type(l))
       logfile.write(message)
       sys.exit(message)
        
###########################################################################
# GET INPUT
###########################################################################

if __name__ == '__main__':
    # Parse input from command line
    parser = ArgumentParser()
    parser.add_argument("-i", dest="input_fastq", help="Fastq file", nargs = "+")
    parser.add_argument("-r", dest="r",help="References you want to map to", nargs = "+")
    parser.add_argument("-g", dest="g",help="Unicycler assembly.gfa file", nargs = "+")
    parser.add_argument("-o", dest="o", help="Output filename")
    parser.add_argument("-f", dest="f",help="Unicycler assembly.fasta file", nargs = "+")
    parser.add_argument("-c", dest="c", help="Circular (True or False)")
    parser.add_argument("-l", dest="l",help="Maximum length of contig")
    args = parser.parse_args()

    # Define input as variables
    input_fastq = args.input_fastq
    r = args.r
    o = args.o
    c = args.c
    l = args.l

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

    # Test c flag
    str2bool(c)

    # Test l flag
    str2int(l)
    
    # Test if fasta references and fastq files is exists in folder
    for file in input_fastq:
        if os.path.exists(file) == False:
            message="Input Error: {} does not exist in path.".format(file)
            logfile.write(message)
            sys.exit(message)

    for file in r:
        if os.path.exists(file) == False:
            message = "Input Error: {} does not exist in path.".format(file)
            logfile.write(message)
            sys.exit(message)

    # Test if references and input files is correct format
    r_check_fasta = CheckFasta(r)

    input_check_fasta = CheckFasta(input_fastq)
    input_check_fastq = CheckFastq(input_fastq)

    # References should be in fasta format
    for i in range(0,len(r_check_fasta)):
        if r_check_fasta[i] == False:
            message = "Input Error: {} is a wrong format. Should be fasta format.".format(r[i])
            logfile.write(message)
            sys.exit(message)

    # Input data should be fastq or fasta format
    for i in range(0,len(input_check_fasta)):
        if input_check_fasta[i] == False and input_check_fastq[i] == False:
            message = "Input Error: {} is a wrong format. Should be fastq or fasta format.".format(input_fastq[i])
            logfile.write(message)
            sys.exit(message)

    # Test Unicycler input if given
    if g:
        for file in g:
            if os.path.exists(file) == False:
                message = "Input Error: {} does not exist in path.".format(file)
                logfile.write(message)
                sys.exit(message)
        for file in f:
            if os.path.exists(file) == False:
                message = "Input Error: {} does not exist in path.".format(file)
                logfile.write(message)
                sys.exit(message)


        ### Check that the input is fasta
        f_check_fasta = CheckFasta(f)
        
        for i in range(0,len(f_check_fasta)):
            if f_check_fasta[i] == False:
                message = "Input Error: {} is a wrong format. Should be fasta format.".format(f[i])
                logfile.write(message)
                sys.exit(message)

        ### Check that the input is gfa
        g_check_gfa = Checkgfa(g)
                
        for i in range(0,len(g_check_gfa)):
                if g_check_gfa[i] == False:
                    message = "Input Error: {} is a wrong format. Should be gfa format.".format(g[i])
                    logfile.write(message)
                    sys.exit(message)

    # Close files
    logfile.close()
