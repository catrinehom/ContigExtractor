#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program: ContigExtractor
Description: This program can find ID corresponding to contigs from a input references in your MinION data.
Step 5: This is the step 5 of the pipeline.
Version: 1.0
Author: Catrine Ahrens Høm
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
    # Input from command line
    parser = ArgumentParser()
    parser.add_argument("-i", dest="input", help="Input file to find IDs from")
    parser.add_argument("-o", dest="o", help="Output filename")
    args = parser.parse_args()

    # Define input as variables
    alignmentfrag = args.input
    o = args.o

    # Open log file
    logname = "{}/{}.log".format(o, o)
    logfile = OpenFile(logname,"a+")

###########################################################################
# FIND IDS
###########################################################################

    # Define ID pattern
    ID_pattern = re.compile(b"\s([\w-]+)\srunid=")


    # Open input file
    infile = OpenFile(alignmentfrag,"rb")

    # Make a set of IDs to make sure they are unique
    ID_set = set()

    # Search after ID and add hits to ID_set
    for line in infile:
        ID_result = re.search(ID_pattern,line)
        if ID_result != None:
            ID_set.add(ID_result.group(1))

    # Close file
    infile.close()

    # Check if any ID is found
    if not ID_set:
        message = "No reads with correct regular expression found in {}!".format(alignmentfrag)
        logfile.write(message)
        sys.exit(message)

###########################################################################
# WRITE RESULT TO FILE
###########################################################################

    # Open output file
    outname = "{}/{}_ID.txt".format(o,o)

    try:
        outfile = open(outname,"w")
    except IOError as error:
        message = "Could not open file due to: {}".format(error)
        logfile.write(message)
        sys.exit(message)


    # Print ID to outfile
    for ID in ID_set:
        print(ID.decode("ascii"), file=outfile)

    # Close files
    outfile.close()
    logfile.close()
