#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program: ContigExtractor
Description: This program can find ID corresponding to contigs from a input references in your MinION data.
Step 2: This is the step 2 of the pipeline.
Version: 1.0
Author: Catrine Ahrens Høm
"""
import sys
import re
from argparse import ArgumentParser

###########################################################################
# STEP 2: Choose this contig in fasta format
###########################################################################

### Get input

# Parse input from command line 
parser = ArgumentParser()
parser.add_argument('-i', '--input', dest='input',help='assembly.gfa file', default='./assemblytest.gfa')
parser.add_argument('-r', '--res', dest='res', help='.res file, output from unicycler', default='./alignmenttest.res')
parser.add_argument('-o', '--output', dest='o', help='output filename')
args = parser.parse_args()

# Define input as variables
filename = args.input
resname = args.res
o = args.o

# THIS SHOULD BE FLAGS
c = True
l = 500000


# Open input files    
try:
    infile = open(filename,'r')
except IOError as error:
    sys.stdout.write('Could not open file due to: '+str(error))
    sys.exit(1)

try:
    resfile = open(resname,'r')
except IOError as error:
    sys.stdout.write('Could not open file due to: '+str(error))
    sys.exit(1)

    
### Find headers for each contig

# Define pattern for information (length, depth, circular)  for header 
Header_gfa_pattern = r'S\t([0-9]*)\t[ATGC]*\tLN:i:([0-9]*)\tdp:f:([0-9.]*)'
#Header_fsa_pattern = r'>([0-9]*)'
Circular_pattern = r'L[\t ]*([0-9]*)[\t ]*[+-][\t ]*([0-9]*)[\t ]*[+-][\t ]*[0-9A-Z]*'

# Define empty set/list
Circular_contig = set()
contignumber = list()
length = list()
depth = list()
Circular = list()

# Search after ID and write header dict
# For gfa file:
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
            
for i in range(1,len(contignumber)+1):
    if str(i) in Circular_contig:
        Circular.append('Yes')
    else:
        Circular.append('No')
          
        
headers = list()

for i in range(0,len(contignumber)):
    headers.append('>Contig'+contignumber[i]+' length='+length[i]+' depth='+depth[i]+' circular='+Circular[i])
    
### Choose contig 

# Define empty list of contigs
matching_contigs = list()

# Skip the header in resfile
next(resfile)

# Look for contig matches in resfile
for line in resfile:
    #matching_contigs.append(line[0].strip())
    matching_contigs.append(re.findall('\d+',line)[0]) 

# Remove empty in contigs
while("" in matching_contigs): 
    matching_contigs.remove("")

    
contig_gfa_pattern = r'S\t([0-9])\t([ATGC]*)'
#contig_fsa_pattern = r'>([0-9]*)'

# Define dict
extracted_contigs = dict()
   
# Open input file
try:
    infile = open(filename,'r')
except IOError as error:
    sys.stdout.write('Could not open file due to: '+str(error))
    sys.exit(1)
 
# Extract contigs in the assembly file
for line in infile:
    contig_gfa_result = re.search(contig_gfa_pattern,line)
    if contig_gfa_result != None: 
        if contig_gfa_result.group(1) in matching_contigs:
            extracted_contigs[contig_gfa_result.group(1)] = contig_gfa_result.group(2)

# Check if contigs is found
if bool(extracted_contigs) is False:
    print('Error! No contigs is found')
    sys.exit(1)
 
keys_to_delete = set()           

# Check if it is circular (if flag is true) and over specified length (defalut = 500.000 bp)
for key in extracted_contigs:
    num = int(key)-1
    if c:
        if key not in Circular_contig:
            print('Contig '+key+' is not circular! It is therefore excluded even though it matched the database.')
            keys_to_delete.add(key)
    if int(length[num]) > l:
        print('Contig '+key+' is over'+str(l)+'bp long! It is therefore excluded even though it matched the database.')
        keys_to_delete.add(key)

# Delete keys that are not circular and over specified length (defalut = 500.000 bp)
for key in keys_to_delete:
    del extracted_contigs[key]
 
# Error message for myself, should not be possible in  final pipeline 
# and should be removed at some point
if len(matching_contigs) != len(extracted_contigs):
    print('Error! Something went completely wrong! \n The assembly.gfa and alignment.res files does not match!')
    sys.exit(1) 

# Open outfile
#contigs_str = '_'.join(extracted_contigs) # If filename should reflect which contigs used?
outname = o+'/assembled_contigs.fasta'

try:
    outfile = open(outname,'w')
except IOError as error:
    sys.stdout.write('Could not open file due to: '+str(error))
    sys.exit(1)   
    

# Print final contig with header to file
for key in extracted_contigs:
    print(headers[int(key)-1],file = outfile)
    print(extracted_contigs[key],file = outfile)

# Close files    
infile.close()
resfile.close()
outfile.close()
