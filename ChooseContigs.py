#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program: ContigExtractor
Description: This program can find ID corresponding to contigs from a input references in your MinION data.
Step 2: This is the step 2 of the pipeline.
Version: 1.0
Author: Catrine Ahrens Høm
Usage: ./ChooseContigs.py -i <Unicycler assembly.gfa file> -r <Result file from BLAST> -o <Output filename> -c <Optional: Exclude non-circular contigs> -l <Optional: Maximum length of contigs>
"""

# Import libraries
import sys
import re
from argparse import ArgumentParser
from ErrorHandling import OpenFile

###########################################################################
# GET INPUT
###########################################################################

if __name__ == '__main__':
    # Parse input from command line
    parser = ArgumentParser()
    parser.add_argument("-i", dest="input",help="Unicycler assembly.gfa file")
    parser.add_argument("-r", dest="res", help="Result file from BLAST")
    parser.add_argument("-o", dest="o", help="Output filename")
    parser.add_argument("-c", dest="c", help="Exclude non-circular contigs")
    parser.add_argument("-l", dest="l", help="Maximum length of contigs", type=int)

    args = parser.parse_args()

    # Define input as variables
    filename = args.input
    resname = args.res
    o = args.o
    c = args.c
    l = args.l

    # Open log file
    logname = "{}/{}.log".format(o, o)
    logfile = OpenFile(logname,"a+")

    # Open input files
    infile = OpenFile(filename,"r")
    resfile = OpenFile(resname,"r")


###########################################################################
# MAKE HEADERS
###########################################################################

    # Define pattern for information (length, depth, circular) for header
    header_gfa_pattern = r"S\t([0-9]*)\t[ATGC]*\tLN:i:([0-9]*)\tdp:f:([0-9.]*)"
    circular_pattern = r"L[\t ]*([0-9]*)[\t ]*[+-][\t ]*([0-9]*)[\t ]*[+-][\t ]*[0-9A-Z]*"

    # Define variables
    circular_contig = set()
    contignumber = list()
    length = list()
    depth = list()
    circular = list()

    # Search for information (length, depth, circular) in gfa file
    for line in infile:
        Header_gfa_result = re.search(header_gfa_pattern,line)
        if Header_gfa_result != None:
            contignumber.append(Header_gfa_result.group(1))
            length.append(Header_gfa_result.group(2))
            depth.append(Header_gfa_result.group(3))

        circular_result = re.search(circular_pattern,line)
        if circular_result != None:
            if circular_result.group(1) == circular_result.group(2):
                circular_contig.add(int(circular_result.group(1)))

    # Close file
    infile.close()

    # Make list of yes/no for each contigs depending on circular information
    for i in range(1,len(contignumber)+1):
        if i in circular_contig:
            circular.append("Yes")
        else:
            circular.append("No")

    # Make final headers
    headers = list()
    for i in range(0,len(contignumber)):
        headers.append(">Contig{} length={} depth={} circular={}".format(contignumber[i], length[i], depth[i], circular[i]))

###########################################################################
# CHOOSE CONTIGS
###########################################################################

    # Define empty list of contigs
    matching_contigs = list()

    # Look for contig matches in resfile
    for line in resfile:
        if line.startswith(">"):
            matching_contigs.append(line.split()[0][1::])

    # Close file
    resfile.close()

    # Define gfa pattern
    contig_gfa_pattern = r"S\t([0-9]*)\t([ATGC]*)"

    # Define variables
    extracted_contigs = dict()

    # Open input file again
    infile = OpenFile(filename,"r")

    # Extract contigs in the gfa file
    for line in infile:
        contig_gfa_result = re.search(contig_gfa_pattern,line)
        if contig_gfa_result != None:
            if contig_gfa_result.group(1) in matching_contigs:
                extracted_contigs[int(contig_gfa_result.group(1))] = contig_gfa_result.group(2)

    # Close file
    infile.close()

    # Check if contigs is found
    if not extracted_contigs:
        message = "Error! No contigs is found matching your reference."
        logfile.write(message)
        sys.exit(message)

    ###########################################################################
    # FILTER CONTIGS
    ###########################################################################

    # Check if it is circular (if flag is true) and over specified length (default = 500.000 bp)
    keys_to_delete = set()

    for key in extracted_contigs:
        num = key-1
        if c:
            if key not in circular_contig:
                message = "Contig{} is not circular! It is therefore excluded even though it matched the database.\n".format(key)
                print(message)
                logfile.write(message)
                keys_to_delete.add(key)
        if int(length[num]) > l:
            message = "Contig{} is over {} bp long! It is therefore excluded even though it matched the database.\n".format(key, l)
            print(message)
            logfile.write(message)
            keys_to_delete.add(key)

    # Delete keys that are not circular and over specified length (default = 500.000 bp)
    for key in keys_to_delete:
        del extracted_contigs[key]

    # Check if any contigs is left after requirement filtering
    if not extracted_contigs:
        message = "Error! No contigs is found matching your reference with requirements length={} and circular={}. \n".format(l, c)
        logfile.write(message)
        sys.exit(message)


###########################################################################
# WRITE RESULT TO FILE
###########################################################################

    # Open output file
    outname = "{}/assembled_contigs.fasta".format(o)

    try:
        outfile = open(outname,"w")
    except IOError as error:
        message = "Could not open file due to: {}".format(error)
        logfile.write(message)
        sys.exit(message)


    # Print final contig with header to file
    for key in extracted_contigs:
        message = "Contig{} matched the references and was under the requirements length={} and circular={}. \n".format(key, l, c)
        print(message)
        logfile.write(message)

        print(headers[int(key)-1],file = outfile)
        print(extracted_contigs[key],file = outfile)

    # Close files
    outfile.close()
    logfile.close()
