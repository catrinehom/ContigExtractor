#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program: ContigExtractor
Description: This program can find ID corresponding to contigs from a input references in your MinION data.
Step 0: This is the error handling of the step 'Get input'
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
parser.add_argument('-i', dest='input_fastq', help='Fastq file', nargs = '+')
parser.add_argument('-r', dest='r',help='References you want to map to', nargs = '+')
parser.add_argument('-g', dest='g',help='Unicycler assembly.gfa file')
parser.add_argument('-o', dest='o', help='Output filename')
parser.add_argument('-f', dest='f',help='Unicycler assembly.fasta file')
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
logname = o+"/"+o+".log"
logfile = OpenFile(logname,"a+")
    
###########################################################################
# TEST INPUT
###########################################################################

# Test if fasta references and fastq files is exists in folder  
for file in input_fastq:
    if os.path.exists(file) == False:
        logfile.write('Input Error: '+file+' does not exist in path.')
        print('Input Error: '+file+' does not exist in path.')
        sys.exit(1)   
    
for file in r: 
    if os.path.exists(file) == False:
        logfile.write('Input Error: '+file+' does not exist in path.')
        print('Input Error: '+file+' does not exist in path.')
        sys.exit(1)
    
# Test if references and input files is correct format
r_check_fasta = CheckFasta(r)

input_check_fasta = CheckFasta(input_fastq)
input_check_fastq = CheckFastq(input_fastq)

# References should be in fasta format
for i in range(0,len(r_check_fasta)):
    if r_check_fasta[i] is False:
        logfile.write('Input Error: '+r[i]+' is a wrong format. Should be fasta format.')
        print('Input Error: '+r[i]+' is a wrong format. Should be fasta format.')
        sys.exit(1)

# Input data should be fastq format (or fasta? Forgot why I thought that would be an option)
for i in range(0,len(input_check_fasta)):
    if input_check_fasta[i] is False and input_check_fastq[i] is False:
        logfile.write(1)
        print('Input Error: '+input_fastq[i]+' is a wrong format. Should be fastq or fasta format.')
        sys.exit('Input Error: '+input_fastq[i]+' is a wrong format. Should be fastq or fasta format.')
 
# Test Unicycler input if given
if args.g:
    if os.path.exists(g) == False:
        logfile.write('Input Error: '+g+' does not exist in path.')
        print('Input Error: '+g+' does not exist in path.')
        sys.exit(1)
        
    if os.path.exists(f) == False:
        logfile.write('Input Error: '+f+' does not exist in path.')
        print('Input Error: '+f+' does not exist in path.')
        sys.exit(1)
    

    ### Check that the input is gfa and fasta
    # Define variables
    fasta_type = '>'
    gfa_type = 'S'
 
    # Open f file and get the first character
    file = open(f, 'r') 
    first_char = file.read(1);
    file.close()
    
    # Check if fasta
    if first_char != fasta_type:
        logfile.write('Error! Unknown format of input file: '+f+'. Should be fasta format.')
        print('Error! Unknown format of input file: '+f+'. Should be fasta format.')
        sys.exit(1)
    
    
    # Open g file and get the first character
    file = open(g, 'r')
    first_char = file.read(1);
    file.close()
    
    # Check if gfa
    if first_char != gfa_type:
        logfile('Error! Unknown format of input file: '+g+'. Should be gfa format')
        print('Error! Unknown format of input file: '+g+'. Should be gfa format')
        sys.exit(1)

# Close files     
logfile.close()

'''
#### SHOULD THIS BE AN OPTION???
# Check input files from command line, else ask for it
if args.input is None:
    filename = input('Please choose a assembly file to load: ')
    plasmidfile = input('Please choose a plasmid references to load: ')
else:
    filename = args.input
    plasmidfiles = args.r
'''

