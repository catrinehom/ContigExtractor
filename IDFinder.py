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
import gzip
from argparse import ArgumentParser

###########################################################################
# FUNCTIONS
###########################################################################

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
        logfile.write('Could not open '+filename+' due to: '+str(error))
        print('Could not open '+filename+' due to: '+str(error))
        sys.exit(1)
    return infile


###########################################################################
# GET INPUT
###########################################################################

# Input from command line
parser = ArgumentParser()
parser.add_argument('-i', dest='input',help='Input file to find IDs from')
parser.add_argument('-o', dest='o', help='Output filename')
args = parser.parse_args()

# Define input as variables
alignmentfrag = args.input
o = args.o

# Open log file
logname = o+"/"+o+".log"
logfile = OpenFile(logname,"a+") 

###########################################################################
# FIND IDS 
###########################################################################

# Define ID pattern
#ID_pattern = b'[ATGC]+\t[0-9]+\t[0-9]+\t[0-9]+\t[0-9]+\t[a-zA-z0-9- .]*\t([a-zA-z0-9-=:]+)'
#ID_pattern = b'([A-Za-z0-9-]*)\srunid='
#ID_pattern = re.compile(b'[\w-]+(?=\s+runid=)')
ID_pattern = re.compile(b'\s([\w-]+)\srunid=')


# Open input file
infile = OpenFile(alignmentfrag,'rb')

# Make a set of IDs to make sure they are unique
ID_set = set()

# Search after ID and write dict
for line in infile:
    ID_result = re.search(ID_pattern,line)
    if ID_result != None: 
        ID_set.add(ID_result.group(1))

# Check if any ID is found
if not ID_set:
    print('No IDs found in '+o+alignmentfrag+'!')
    logfile.write('No IDs found in '+o+alignmentfrag+'!')

###########################################################################
# WRITE RESULT TO FILE
###########################################################################

# Open output file
outname = o+'/'+o+'_ID.txt'
#outfile = OpenFile(outname,'w')

try:
    outfile = open(outname,'w')
except IOError as error:
    sys.stdout.write('Could not open file due to: '+str(error))
    sys.exit(1)
    

# Print ID to outfile        
for ID in ID_set:       
    print(ID.decode('ascii'),file=outfile)

# Close files
infile.close()            
outfile.close()
logfile.close()
