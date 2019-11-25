# ContigExtractor

ContigExtractor is a pipeline to find read ID's from contigs from Nanopore MinION sequencing matching input references. 

## Requirements

- KMA
- Unicycler

## Installation

The following instructions will install the latest version of ContigExtractor:

```
git clone https://github.com/catrinehom/ContigExtractor.git

cd ContigExtractor/

chmod a+x ContigExtractor.sh
chmod a+x ChooseContigs.py
chmod a+x IDFinder.py
chmod a+x ErrorHandling.py
```

### Move to bin 
You might want to move the program to your bin to make the program globally excecutable. 
The placement of your bin depends on your system configuration, but common paths is:

```
/usr/local/bin/
```
OR
```
~/bin/
```

Example of move to bin:

```
mv ContigExtractor.sh /usr/local/bin/
mv ChooseContigs.py /usr/local/bin/
mv IDFinder.py /usr/local/bin/
mv ErrorHandling.py /usr/local/bin/
```

## Usage

To run full pipeline:

```
./ContigExtractor.sh [-i <fastq filename>] [-r <references filename>] [-o <output filename>]
```

If you already ran Unicycler you can input the assembly files:
```
./ContigExtractor.sh [-i <fastq filename>] [-r <references filename>] [-o <output filename>] [-g <Unicycler assembly.gfa>] [-f <Unicycler assembly.fasta>]
```

## Pipeline overview

![alt text](https://github.com/catrinehom/ContigIdentifyer/blob/master/SSI_pipeline_overview2.png)
