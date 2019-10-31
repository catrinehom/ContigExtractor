#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#Program: SegmentIdentifier
#Description: This program can find ID corresponding to segments from an input database in your MinION data.
Step 5: This is the step 5 of the pipeline.
#Version: 1.0
#Author: Catrine Ahrens Høm

#Usage:
    ## SegmentIdentifier.sh [-i] <MinION reads in fastq format> [-d] <Database of wanted segments in fasta format>
    ## -i --input: MinION filename path relative to current working directory.
    ## -d --database: Database filename path relative to current working directory.
    ## ID.txt will be available in the working directory after run.

#This pipeline consists of 5 steps:
    ## STEP 1:  Unicycler (Skipped if assembly file is supplied)
    ## STEP 2:  Find the segments which match database
    ## STEP 3:  Choose this segment in fsa fragment
    ## STEP 4:  KMA fragment against reads
    ## STEP 5:  Find IDs and save to file
"""
import sys
import re
import gzip
from argparse import ArgumentParser

def CheckGZip(filename):
    '''
    This function checks if the input file is gzipped.
    '''
    gzipped_type = b'\x1f\x8b'
    
    infile = open(filename,'rb')
    filetype = infile.read(2)
    infile.close()
    if filetype == gzipped_type:
        return True
    else:
        return False
    
def OpenFile(filename,mode):
    '''
    This function opens the input file in chosen mode.
    '''
    try:
        if CheckGZip(filename):
            infile = gzip.open(filename,mode) 
        else:
            infile = open(filename,mode)   
    except IOError as error:
        sys.exit('Can\'t open file, reason:',str(error),'\n') 
    return infile

# Input from command line
parser = ArgumentParser()
parser.add_argument('-i', '--input', dest='input',help='Input file to find IDs from', default='./reads_alignment.frag.gz')
args = parser.parse_args()
alignmentfrag = str(args.input)


# Define ID pattern
#ID_pattern = b'[ATGC]+\t[0-9]+\t[0-9]+\t[0-9]+\t[0-9]+\t[a-zA-z0-9- .]*\t([a-zA-z0-9-=:]+)'
#ID_pattern = b'([A-Za-z0-9-]*)\srunid='
#ID_pattern = re.compile(b'[\w-]+(?=\s+runid=)')
ID_pattern = re.compile(b'\s([\w-]+)\srunid=')


# Open input file
infile = OpenFile(alignmentfrag,'rb')

# Open output file
outfilename = './ID.txt'

try:
    outfile = open(outfilename,'w')
except IOError as error:
    sys.stdout.write('Could not write file due to: '+str(error))
    sys.exit(1)


# Make a set of IDs to make sure they are unique
ID_set = set()

# Search after ID and write dict
for line in infile:
    ID_result = re.search(ID_pattern,line)
    if ID_result != None: 
        ID_set.add(ID_result.group(1))

# Check if any ID is found
if not ID_set:
    print('No IDs found in '+alignmentfrag+'!')

# Print ID to outfile        
for ID in ID_set:       
    print(ID.decode('ascii'),file=outfile)

# Close files
infile.close()            
outfile.close()

