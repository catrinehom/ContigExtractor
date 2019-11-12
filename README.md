# ContigExtractor

ContigExtractor is a pipeline to find read ID's from Nanopore MinION sequencing matching an input database. 

## Requirements

- KMA
- Unicycler

## Usage

To run full pipeline:

./ContigExtractor.sh [-i \<fastq filename\>] [-r \<references filename\>] [-o \<output filename\>]

If you already ran Unicycler you can input the assembly files:

./ContigExtractor.sh [-i \<fastq filename\>] [-r \<references filename\>] [-o \<output filename\>] [-g \<Unicycler assembly.gfa\>] [-f \<Unicycler assembly.fasta\>]

## Pipeline overview

![alt text](https://github.com/catrinehom/ContigIdentifyer/blob/master/SSI_pipeline_overview.png)
