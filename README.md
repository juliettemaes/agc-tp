# Abundance Greedy Clustering and operational taxonomic unit (OTU) Calculation

You can find the complete description of the practical work [here](https://docs.google.com/document/d/1qWNqPZ9Ecd-yZ5Hpl6n2zd7ZGtHPjf3yaW1ulKRdWnk/edit?usp=sharing).

## Introduction

The objective of this work is to calculate the OTUs obtained from a "mock" sequencing. Only bacterial sequences (not fungi) were amplified, and thus 8 species are expected.

The program performs full-length sequence deduplication ("dereplication full length"), chimeric sequence detection, and clustering based on a greedy algorithm ("Abundance Greedy Clustering").

## Installing Dependencies

You will use the Python libraries nwalign3, pytest, and pylint:
```
conda create -n agc python=3.8 pip numpy
conda activate agc
conda install -c conda-forge -c bioconda -c defaults numpy nwalign3 pytest pylint pytest-cov
```

## Usage

This program performs full-length sequence deduplication ("dereplication full length"), chimeric sequence detection, and clustering based on a greedy algorithm ("Abundance Greedy Clustering"). 
Run agc/agc.py script, with the following arguments :
- -i, -amplicon_file file containing sequences in FASTA format
- -s, -minseqlen minimum sequence length (optional - default value 400)
- -m, -mincount minimum sequence count (optional - default value 10)
- -c, -chunk_size sequence partition size (optional - default value 100)
- -k, -kmer_size kmer length (optional - default value 8)
- -o, -output_file output file with OTUs in FASTA format
