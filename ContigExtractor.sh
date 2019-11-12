#!/usr/bin/env bash

#Program: ContigExtractor
#Description: This program can find ID corresponding to contigs from a input references in your MinION data.
#Version: 1.0
#Author: Catrine Ahrens Høm

#Usage:
    ## ContigExtractor.sh [-i] <MinION reads in fastq format> [-d] <Reference(s) of wanted contigs in fasta format>
    ## -i --input: MinION filename path.
    ## -d --database: Reference filename path.
    ## ID.txt will be available in the working directory after run.

#This pipeline consists of 5 steps:
    ## STEP 1:  Unicycler (Skipped if assembly file is supplied)
    ## STEP 2:  Find the contigs which match references
    ## STEP 3:  Choose this contig in fasta fragment
    ## STEP 4:  KMA fragment against reads
    ## STEP 5:  Find IDs and save to file


###########################################################################
# GET INPUT
###########################################################################
# load an enviroment
#source activate sovp_test

# How to use program
usage() { echo "Usage: $0 [-i <fastq filename>] [-r <references filename>] [-o <outputname>] [-g <Unicycler assembly.gfa] [-f assembly.fasta>]" 1>&2; exit 1; }

# Parse flags
while getopts ":i:r:o:g:f:h" opt; do
    case "${opt}" in
        i)
            i=${OPTARG}
            ;;
        r)
            r=${OPTARG}
            ;;
        o)
            o=${OPTARG}
            ;;
        g)
            g=${OPTARG}
            ;;
        f)
            f=${OPTARG}
            ;;
    
        h) 
            usage
            ;;
        *)
            echo "Invalid option: ${OPTARG}"
            usage
            ;;
    esac
done
shift $((OPTIND-1))


# Check if required flags are empty
if [ -z "${i}" ] || [ -z "${r}" ] || [ -z "${o}" ]; then
    echo "i, r and o are required flags"
    usage
fi

# Make output directory
[ -d $o ] && echo "Output directory: ${o} already exists. Files will be overwritten"|| mkdir $o


# Check format and that the files exists
if [ -z "${g}" ] || [ -z "${f}" ]; then
  ./ErrorHandling.py -i $i -r $r
else
  ./ErrorHandling.py -i $i -r $r -g $g -f $f
fi

# Check if python script exited with an error
if [ $? -eq 0 ]
then
  echo "Error handling of input done."
else
  # Redirect stdout from echo command to stderr.
  echo "Script exited due to input error." >&2
  exit 1
fi

# Print files used
echo "Input used is ${i}"
echo "References used is ${r}"

###########################################################################
# STEP 1: Unicycler
###########################################################################
# Run only Unicycler if no input is given
if [ -z "${g}" ] || [ -z "${f}" ]; then
  echo "Starting STEP 1: Unicycler"

  #Hardcoded, should maybe be flags
  t=8
  mem=24

  # Define output names
  u="/"$o".unicycler.nponly"
  g=$o$u"/assembly.gfa"
  f=$o$u"/assembly.fasta"

  source activate unicycler_v0.4.7_no_stall
  /srv/data/tools/git.repositories/Unicycler/unicycler-runner.py -t $t -l $i -o $o$u --keep 0

  echo "$u is saved in current working directory."
else
    echo "STEP 1 is skipped due to already inputted Unicycler assembly."
    echo "Unicycler assembly used is ${g} and ${f}"
fi

###########################################################################
# STEP 2: FIND WHICH CONTGS IS THE WANTED CONTIGS
###########################################################################

echo "Starting STEP 2: "

source activate sovp_test
mkdir $o/databases
kma index -i $f -o $o/databases/contigs_database
kma -i $r -o $o/contigs_alignment -t_db $o/databases/contigs_database -mrs 0.5

###########################################################################
# STEP 3: Choose this contig in fasta format
###########################################################################

echo "Starting STEP 3: "

./ChooseContigs.py -r $o/contigs_alignment.res -i $g -o $o

# Check if python script exited with an error
if [ $? -eq 0 ]
then
  echo "Contig(s) identified in input file."
else
  # Redirect stdout from echo command to stderr.
  echo "Script exited due to error." >&2
  exit 1
fi

###########################################################################
# STEP 4:  KMA reads against contigs
###########################################################################

echo "Starting STEP 4: "

#Command used to index plasmid database:
kma index -i $o/assembled_contigs.fasta -o $o/databases/reads_database

#Command to run KMA:
kma -i $i -o $o/reads_alignment -t_db $o/databases/reads_database -mrs 0.1 -bcNano -mp 20 -mem_mode

###########################################################################
# STEP 5:  Find IDs and save to file
###########################################################################

echo "Starting STEP 5: "

./IDFinder.py -i $o/reads_alignment.frag.gz -o $o

# Check if python script exited with an error
if [ $? -eq 0 ]
then
  echo "IDs found! ID.txt is saved in working directory."
else
  # Redirect stdout from echo command to stderr.
  echo "No IDs found!" >&2
fi
