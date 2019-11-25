#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program: ContigExtractor
Description: This program can find ID corresponding to contigs from a input references in your MinION data.
Step 2: This is the step 2 of the pipeline.
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

# Parse input from command line 
parser = ArgumentParser()
parser.add_argument('-i', '--input', dest='input',help='assembly.gfa file', default='./assemblytest.gfa')
parser.add_argument('-r', '--res', dest='res', help='result file from BLAST', default='./blast_result.out')
parser.add_argument('-o', '--output', dest='o', help='output filename')
parser.add_argument('-c', '--circular', dest='c', help='Exclude non-circular contigs', default=True)
parser.add_argument('-l', '--length', dest='l', help='Max length of contigs', default=500000)

args = parser.parse_args()

# Define input as variables
filename = args.input
resname = args.res
o = args.o
c = args.c
l = args.l

# Open log file
logname = o+"/"+o+".log"
logfile = OpenFile(logname,"a+")

# Open input files   
infile = OpenFile(filename,'r') 
resfile = OpenFile(resname,'r')
    
    
###########################################################################
# MAKE HEADERS
###########################################################################

# Define pattern for information (length, depth, circular) for header 
Header_gfa_pattern = r'S\t([0-9]*)\t[ATGC]*\tLN:i:([0-9]*)\tdp:f:([0-9.]*)'
#Header_fsa_pattern = r'>([0-9]*)'
Circular_pattern = r'L[\t ]*([0-9]*)[\t ]*[+-][\t ]*([0-9]*)[\t ]*[+-][\t ]*[0-9A-Z]*'

# Define variables
Circular_contig = set()
contignumber = list()
length = list()
depth = list()
Circular = list()

# Search for information (length, depth, circular) in gfa file
for line in infile:
    Header_gfa_result = re.search(Header_gfa_pattern,line)       
    if Header_gfa_result != None: 
        contignumber.append(Header_gfa_result.group(1))
        length.append(Header_gfa_result.group(2))
        depth.append(Header_gfa_result.group(3))
          
    Circular_result = re.search(Circular_pattern,line)
    if Circular_result != None:
        if Circular_result.group(1) == Circular_result.group(2):
            Circular_contig.add(Circular_result.group(1))

# Make list of yes/no for each contigs depending on circular information          
for i in range(1,len(contignumber)+1):
    if str(i) in Circular_contig:
        Circular.append('Yes')
    else:
        Circular.append('No')
          
# Make final headers        
headers = list()
for i in range(0,len(contignumber)):
    headers.append('>Contig'+contignumber[i]+' length='+length[i]+' depth='+depth[i]+' circular='+Circular[i])
    
###########################################################################
# CHOOSE CONTIGS
###########################################################################

# Define empty list of contigs
matching_contigs = list()

# Look for contig matches in resfile
for line in resfile:
    if line.startswith('>'):
        matching_contigs.append(line.split()[0][1::])


# Remove empty in contigs
#while("" in matching_contigs): 
#    matching_contigs.remove("")
        
    
contig_gfa_pattern = r'S\t([0-9]*)\t([ATGC]*)'
#contig_fsa_pattern = r'>([0-9]*)'

# Define dict
extracted_contigs = dict()
   
# Open input file again
infile = OpenFile(filename,'r') 
 
# Extract contigs in the gfa file
for line in infile:
    contig_gfa_result = re.search(contig_gfa_pattern,line)
    if contig_gfa_result != None: 
        if contig_gfa_result.group(1) in matching_contigs:
            extracted_contigs[contig_gfa_result.group(1)] = contig_gfa_result.group(2)

# Check if contigs is found
if bool(extracted_contigs) is False:
    print('Error! No contigs is found matching your reference.')
    logfile.write('Error! No contigs is found matching your reference.')
    sys.exit(1)
           
###########################################################################
# FILTER CONTIGS
###########################################################################

# Check if it is circular (if flag is true) and over specified length (defalut = 500.000 bp)
keys_to_delete = set() 

for key in extracted_contigs:
    num = int(key)-1
    if c:
        if key not in Circular_contig:
            print('Contig '+key+' is not circular! It is therefore excluded even though it matched the database.')
            logfile.write('Contig '+key+' is not circular! It is therefore excluded even though it matched the database.')
            keys_to_delete.add(key)
    if int(length[num]) > l:
        print('Contig '+key+' is over '+str(l)+'bp long! It is therefore excluded even though it matched the database.')
        logfile.write('Contig '+key+' is over '+str(l)+'bp long! It is therefore excluded even though it matched the database.')
        keys_to_delete.add(key)

# Delete keys that are not circular and over specified length (default = 500.000 bp)
for key in keys_to_delete:
    del extracted_contigs[key]
    
# Check if any contigs is left after requirement filtering
if bool(extracted_contigs) is False:
    print('Error! No contigs is found Error! No contigs is found matching your reference with requirements length='+str(l)+' and circular='+str(c))
    logfile.write('Error! No contigs is found Error! No contigs is found matching your reference with requirements length='+str(l)+' and circular='+str(c))
    sys.exit(1)
 

###########################################################################
# WRITE RESULT TO FILE
###########################################################################

# Open outfile
#contigs_str = '_'.join(extracted_contigs) # If filename should reflect which contigs used?

# Open output file 
outname = o+'/assembled_contigs.fasta'
outfile = OpenFile(outname,'w')

# Print final contig with header to file
for key in extracted_contigs:
    print(headers[int(key)-1],file = outfile)
    print(extracted_contigs[key],file = outfile)

# Close files    
infile.close()
resfile.close()
outfile.close()
logfile.close()
