#!/usr/bin/env bash

#Program: ContigExtractor
#Description: This program can find ID corresponding to contigs from a input references in your MinION data.
#Version: 1.0
#Author: Catrine Ahrens Høm

#Usage:
    ## ./ContigExtractor.sh [-i <fastq filename>] [-r <references filename>] [-o <outputname>] [-g <optional Unicycler assembly.gfa>] [-f <optional Unicycler assembly.fasta>]
    ## -i, fastq file path
    ## -r, reference file path
    ## -t, threads for Unicycler and kma, default=8
    ## -c circular contigs output only, default="True"
    ## -l length (maximum) of contigs, default=500000
    ## An ID list will be available after succesfull run.

#This pipeline consists of 5 steps:
    ## STEP 1:  Unicycler (Skipped if assembly file is supplied)
    ## STEP 2:  Find the contigs which match references
    ## STEP 3:  Choose these contigs in fasta format
    ## STEP 4:  Align fastq reads against contigs
    ## STEP 5:  Find IDs for aligned fastq reads


###########################################################################
# GET INPUT
###########################################################################

# Start timer for logfile
SECONDS=0

# How to use program
usage() { echo "Usage: $0 [-i <fastq filename>] [-r <references filename>] [-o <outputname>] [-g <optional Unicycler assembly.gfa>] [-f <optional Unicycler assembly.fasta>]" 1>&2; exit 1; }

# Default values
t=8
c="True"
l=500000

# Parse flags
while getopts ":i:r:o:g:f:h:t:c:l" opt; do
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
        t)
            t=${OPTARG}
            ;;
        c)
            c=${OPTARG}
            ;;
        l)
            l=${OPTARG}
            ;;
        h)
            usage
            echo "Optional flags:"
            echo "-t threads for Unicycler, default=8"
            echo "-c circular contigs output only, default='True'"
            echo "-l maximum length of contigs, default=500000"
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
[ -d $o ] && echo "Output directory: ${o} already exists. Files will be overwritten."  | tee -a $log || mkdir $o

# Make logfile and empty it
log=${o}/${o}.log
touch $log
cat /dev/null > $log

date=$(date "+%Y-%m-%d %H:%M:%S")
echo "Starting ContigExtractor ($date)" | tee -a $log
echo "-----------------------------------------------" | tee -a $log
echo "ContigExtractor is a pipeline to find read ID's from contigs from Nanopore MinION sequencing matching input references." | tee -a $log
echo "" | tee -a $log

# Check format and that the files exists
if [ -z "${g}" ] || [ -z "${f}" ]; then
  ./ErrorHandling.py -i $i -r $r -o $o
else
  ./ErrorHandling.py -i $i -r $r -o $o -g $g -f $f
fi

# Check if python script exited with an error
if [ $? -eq 0 ]
then
  echo "Error handling of input done." | tee -a $log
else
  # Redirect stdout from echo command to stderr.
  echo "Script exited due to input error." | tee -a $log
  exit 1
fi

# Print files used
echo "Input used is ${i}" | tee -a $log
echo "References used is ${r}" | tee -a $log

echo "Time stamp: $SECONDS seconds." | tee -a $log
echo "" | tee -a $log

###########################################################################
# STEP 1: Unicycler
###########################################################################
# Run only Unicycler if no input is given
if [ -z "${g}" ] || [ -z "${f}" ]; then
  echo "Starting STEP 1: Unicycler" | tee -a $log

  # Define output names
  u="/"$o".unicycler.nponly"
  g=$o$u"/assembly.gfa"
  f=$o$u"/assembly.fasta"

  unicycler -t $t -l $i -o $o$u --keep 0

  echo "$u created with assembly in fasta and gfa format." | tee -a $log
else
    echo "STEP 1 is skipped due to already inputted Unicycler assembly." | tee -a $log
    echo "Unicycler assembly used is ${g} and ${f}" | tee -a $log
fi

echo "Time stamp: $SECONDS seconds." | tee -a $log
echo "" | tee -a $log

###########################################################################
# STEP 2: FIND WANTED CONTGS
###########################################################################

echo "Starting STEP 2: Find wanted contigs" | tee -a $log

cdb="contigs_database"
res="blast_results.out"
mkdir $o/databases
makeblastdb -in $f -parse_seqids -title $cdb -dbtype nucl -out $o/databases/$cdb
blastn -db $o/databases/$cdb -query $r -out $o/$res

echo "blast_results.out created with information on contigs aligning with references." | tee -a $log
echo "Time stamp: $SECONDS seconds." | tee -a $log
echo "" | tee -a $log

###########################################################################
# STEP 3: CHOOSE CONTIGS
###########################################################################

echo "Starting STEP 3: Choose Contigs" | tee -a $log

./ChooseContigs.py -r $o/$res -i $g -o $o -c $c -l $l

# Check if python script exited with an error
if [ $? -eq 0 ]
then
  echo "Contig(s) identified in input file." | tee -a $log
else
  echo "Script exited due to error." | tee -a $log
  exit 1
fi

echo "Time stamp: $SECONDS seconds." | tee -a $log
echo "" | tee -a $log

###########################################################################
# STEP 4:  KMA READS AGAINST CONTIGS
###########################################################################

echo "Starting STEP 4: KMA reads against contigs." | tee -a $log

#Command used to index plasmid database:
kma index -i $o/assembled_contigs.fasta -o $o/databases/reads_database

#Command to run KMA:
kma -i $i -o $o/reads_alignment -t_db $o/databases/reads_database -mrs 0.5 -bcNano -mp 20 -mem_mode -t $t -1t1

echo "Time stamp: $SECONDS seconds." | tee -a $log
echo "" | tee -a $log

###########################################################################
# STEP 5:  FIND IDs
###########################################################################

echo "Starting STEP 5: Find IDs" | tee -a $log

./IDFinder.py -i $o/reads_alignment.frag.gz -o $o

# Check if python script exited with an error
if [ $? -eq 0 ]
then
  echo "IDs found! ${o}_ID.txt is saved in ${o} directory." | tee -a $log
else
  echo "No IDs found!" | tee -a $log
fi

echo "Time stamp: $SECONDS seconds." | tee -a $log
