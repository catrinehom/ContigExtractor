#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#Program: SegmentIdentifier
#Description: This program can find ID corresponding to segments from an input database in your MinION data.
Step 0: This is the error handling of the step 'Get input'
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

# Import libraries 
import sys
import os
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
        sys.exit('Cant open file, reason:',str(error),'\n') 
    return infile

def CheckFastq(filenames):
    '''
    This function checks if all input files (list) are in fastq format.
    Outputs a list of True/False for each file.
    '''
    fastq = list() 
    fastq_type = b'@'
    
    # Open all files and get the first character
    for infile in filenames:       
        f = OpenFile(infile, 'rb')
        first_char = f.read(1);
        f.close()
        # Check if fastq
        if first_char == fastq_type:
            fastq.append(True)
        else:
            fastq.append(False)
    return fastq
        
def CheckFasta(filenames):  
    '''
    This function checks if all the input files (list) are in fasta format.
    Outputs a list of True/False for each file.
    ''' 
    fasta = list()
    fasta_type = b'>'
    
    # Open file and get the first character
    for infile in filenames:
        f = OpenFile(infile, 'rb')
        first_char = f.read(1);
        f.close()
        # Check if fasta
        if first_char == fasta_type:
            fasta.append(True)
        else:
            fasta.append(False)
    return fasta

###########################################################################
# GET INPUT
###########################################################################

# Parse input from command line 
parser = ArgumentParser()
parser.add_argument('-i', '--input', dest='input_fastq', help='Fastq file', nargs = '+')
parser.add_argument('-d', '--database', dest='db',help='Database of sequence you want to examine', nargs = '+')
parser.add_argument('-ug', dest='ug',help='Unicycler assembly.gfa file')
parser.add_argument('-uf', dest='uf',help='Unicycler assembly.fasta file')
args = parser.parse_args()

# Define input as variables
input_fastq = args.input_fastq
db = args.db

if args.ug:
    ug = args.ug
    
if args.uf:
    uf = args.uf

# Test if fasta database and fastq files is exists in folder  
for file in input_fastq:
    if os.path.exists(file) == False:
        sys.exit('Input Error: '+file+' does not exist in path.')   
    
for file in db: 
    if os.path.exists(file) == False:
        sys.exit('Input Error: '+file+' does not exist in path.')
    
# Test if database and input files is correct format
db_check_fasta = CheckFasta(db)

input_check_fasta = CheckFasta(input_fastq)
input_check_fastq = CheckFastq(input_fastq)

# Database should be in fasta format
for i in range(0,len(db_check_fasta)):
    if db_check_fasta[i] is False:
        sys.exit('Input Error: '+db[i]+' is a wrong format. Should be fasta format.')

# Input data should be fastq format (or fasta? Forgot why I thought that would be an option)
for i in range(0,len(input_check_fasta)):
    if input_check_fasta[i] is False and input_check_fastq[i] is False:
        sys.exit('Input Error: '+input_fastq[i]+' is a wrong format. Should be fastq or fasta format.')
 
# Test Unicycler input if given
if args.ug:
    if os.path.exists(ug) == False:
        sys.exit('Input Error: '+ug+' does not exist in path.')
    if os.path.exists(uf) == False:
        sys.exit('Input Error: '+uf+' does not exist in path.')
    

    ### Check that the input is gfa and fasta
    # Define variables
    fasta_type = '>'
    gfa_type = 'S'
 
    # Open uf file and get the first character
    f = open(uf, 'r') 
    first_char = f.read(1);
    f.close()
    
    # Check if fsa
    if first_char != fasta_type:
        print('Error! Unknown format of input file: '+uf+'. Should be fasta format')
        sys.exit(1)
    
    
    # Open ug file and get the first character
    f = open(ug, 'r')
    first_char = f.read(1);
    f.close()
    
    # Check if gfa
    if first_char != gfa_type:
        print('Error! Unknown format of input file: '+ug+'. Should be gfa format')
        sys.exit(1)
    

'''
#### SHOULD THIS BE AN OPTION???
# Check input files from command line, else ask for it
if args.input is None:
    filename = input('Please choose a assembly file to load: ')
    plasmidfile = input('Please choose a plasmid database to load: ')
else:
    filename = args.input
    plasmidfiles = args.db
'''

