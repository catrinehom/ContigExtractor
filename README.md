# ContigIdentifyer

ContigIdentifyer is pipeline to find read ID's from Nanopore MinION sequencing matching an input database. 

## Usage

To run full pipeline:

./ContigIdentifyer.sh [-i \<fastq filename\>] [-d \<database filename\>]

If you already ran Unicycler you can input the assembly files:

./ContigIdentifyer.sh [-i \<fastq filename\>] [-d \<database filename\>] [-g \<Unicycler assembly.gfa\>] [-f \<assembly.fasta\>]

## Pipeline overview

![alt text](https://github.com/catrinehom/ContigIdentifyer/blob/master/SSI_pipeline_overview.png)
