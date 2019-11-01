#!/usr/bin/env bash

#Program: SegmentIdentifier
#Description: This program can find ID corresponding to segments from an input database in your MinION data.
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


###########################################################################
# GET INPUT
###########################################################################
# load an enviroment
#source activate sovp_test

# How to use program
usage() { echo "Usage: $0 [-i <fastq filename>] [-d <database filename>] [-g <Unicycler assembly.gfa] [-f assembly.fasta>]" 1>&2; exit 1; }

# Parse flags
while getopts ":i:d:g:f:" o; do
    case "${o}" in
        i)
            i=${OPTARG}
            ;;
        d)
            d=${OPTARG}
            ;;
        g)
            ug=${OPTARG}
            ;;
        f)
            uf=${OPTARG}
            ;;
        *)
            echo "parse flags"
            usage
            ;;
    esac
done
shift $((OPTIND-1))

# Check if required flags are empty
if [ -z "${i}" ] || [ -z "${d}" ]; then
    echo "required flags"
    usage
fi

# Check format and that the files exists
if [ -z "${ug}" ] || [ -z "${uf}" ]; then
  ./ErrorHandling.py -i $i -d $d
else
  ./ErrorHandling.py -i $i -d $d -ug $ug -uf $uf
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
echo "Database used is ${d}"

###########################################################################
# STEP 1: Unicycler
###########################################################################
# Run only Unicycler if no input is given
if [ -z "${ug}" ] || [ -z "${uf}" ]; then
  echo "Starting STEP 1: Unicycler"

  #Hardcoded, should maybe be flags
  t=8
  mem=24

  # Define output from input name + new name
  isolatepath=${i%%.*}
  isolate=$(basename $isolatepath)
  o="./"$isolate".unicycler.nponly"
  ug=$o"/assembly.gfa"
  uf=$o"/assembly.fasta"

  source activate unicycler_v0.4.7_no_stall
  /srv/data/tools/git.repositories/Unicycler/unicycler-runner.py -t $t -l $i -o $o --keep 0

  echo "$o is saved in current working directory."
else
    echo "STEP 1 is skipped due to already inputted Unicycler assembly."
    echo "Unicycler assembly used is ${ug} and ${uf}"
fi

###########################################################################
# STEP 2: FIND WHICH SEGMENT IS THE WANTED SEGMENT
###########################################################################

echo "Starting STEP 2: "

#/srv/data/AS/CTHM/data/CPO20140039.unicycler.nponly.q8/assembly.fasta

source activate sovp_test
mkdir databases
kma index -i $uf -o databases/segment_database
kma -i $d -o ./segment_alignment -t_db ./databases/segment_database -mrs 0.5 -bcNano

###########################################################################
# STEP 3: Choose this segment in fsa format
###########################################################################

echo "Starting STEP 3: "

./ChooseContig.py -r ./segment_alignment.res -i $ug

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
# STEP 4:  KMA fragment against reads
###########################################################################

echo "Starting STEP 4: "

#Command used to index plasmid database:
kma index -i assembled_contigs.fsa -o databases/reads_database

#Command to run KMA:
#./kma -i ../wetransfer-085249/CPO20140039.chop.q8.fastq.gz -o ../data/tmp/alignment -t_db ../data/tmp/plasmiddatabase -mem_mode -mrs 0.01 -bcNano
kma -i $i -o ./reads_alignment -t_db ./databases/reads_database -mrs 0.5 -bcNano

###########################################################################
# STEP 5:  Find IDs and save to file
###########################################################################

echo "Starting STEP 5: "

./IDFinder.py -i ./reads_alignment.frag.gz

# Check if python script exited with an error
if [ $? -eq 0 ]
then
  echo "IDs found! ID.txt is saved in working directory."
else
  # Redirect stdout from echo command to stderr.
  echo "No IDs found!" >&2
fi
