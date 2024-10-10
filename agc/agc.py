#!/bin/env python3
# -*- coding: utf-8 -*-
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    A copy of the GNU General Public License is available at
#    http://www.gnu.org/licenses/gpl-3.0.html

"""OTU clustering"""

import argparse
import sys
import os
import gzip
import statistics
import textwrap
from pathlib import Path
from collections import Counter
from typing import Iterator, Dict, List
# https://github.com/briney/nwalign3
# ftp://ftp.ncbi.nih.gov/blast/matrices/
import nwalign3 as nw

__author__ = "Juliette Maes"
__copyright__ = "Universite Paris Cité"
__credits__ = ["Juliette Maes"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Juliette Maes"
__email__ = "juliette.maes@etu.u-paris.fr"
__status__ = "Developpement"



def isfile(path: str) -> Path:  # pragma: no cover
    """Check if path is an existing file.

    :param path: (str) Path to the file

    :raises ArgumentTypeError: If file does not exist

    :return: (Path) Path object of the input file
    """
    myfile = Path(path)
    if not myfile.is_file():
        if myfile.is_dir():
            msg = f"{myfile.name} is a directory."
        else:
            msg = f"{myfile.name} does not exist."
        raise argparse.ArgumentTypeError(msg)
    return myfile


def get_arguments(): # pragma: no cover
    """Retrieves the arguments of the program.

    :return: An object that contains the arguments
    """
    # Parsing arguments
    parser = argparse.ArgumentParser(description=__doc__, usage=
                                     "{0} -h"
                                     .format(sys.argv[0]))
    parser.add_argument('-i', '-amplicon_file', dest='amplicon_file', type=isfile, required=True,
                        help="Amplicon is a compressed fasta file (.fasta.gz)")
    parser.add_argument('-s', '-minseqlen', dest='minseqlen', type=int, default = 400,
                        help="Minimum sequence length for dereplication (default 400)")
    parser.add_argument('-m', '-mincount', dest='mincount', type=int, default = 10,
                        help="Minimum count for dereplication  (default 10)")
    parser.add_argument('-o', '-output_file', dest='output_file', type=Path,
                        default=Path("OTU.fasta"), help="Output file")
    return parser.parse_args()


def read_fasta(amplicon_file: Path, minseqlen: int) -> Iterator[str]:
    """Read a compressed fasta and extract all fasta sequences.

    :param amplicon_file: (Path) Path to the amplicon file in FASTA.gz format.
    :param minseqlen: (int) Minimum amplicon sequence length
    :return: A generator object that provides the Fasta sequences (str).
    """
    with gzip.open(amplicon_file, 'rt') as f:
        sequence = ""
        for line in f:
            if line.startswith(">"):
                if len(sequence) >= minseqlen:
                    yield sequence
                sequence = ""
            else:
                sequence += line.strip()

        # Handle the last sequence
        if len(sequence) >= minseqlen:
            yield sequence

def dereplication_fulllength(amplicon_file: Path, minseqlen: int, mincount: int) -> Iterator[List]:
    """Dereplicate the set of sequence

    :param amplicon_file: (Path) Path to the amplicon file in FASTA.gz format.
    :param minseqlen: (int) Minimum amplicon sequence length
    :param mincount: (int) Minimum amplicon count
    :return: A generator object that provides a (list)[sequences, count] of sequence with a count >= mincount and a length >= minseqlen.
    """
    # Create empty dictionary
    seq_dict = {}
    # Read the fasta file
    for sequence in read_fasta(amplicon_file, minseqlen):
        if sequence in seq_dict:
            seq_dict[sequence] += 1
        else:
            seq_dict[sequence] = 1
    # Order the dictionary by count (decreasing)
    seq_dict = sorted(seq_dict.items(), key=lambda item: item[1], reverse=True)
    print("-------------------seq_dict-------------------")
    print(seq_dict)
    print("--------------------------------------------")   
    # Return the sequences as a generator
    for sequence, count in seq_dict:
        if count >= mincount:
            yield [sequence, count]



def get_identity(alignment_list: List[str]) -> float:
    """Compute the identity rate between two sequences

    :param alignment_list:  (list) A list of aligned sequences in the format ["SE-QUENCE1", "SE-QUENCE2"]
    :return: (float) The rate of identity between the two sequences.
    """
    id_count = 0
    for index, aa in enumerate(alignment_list[0]):
        if aa == alignment_list[1][index]:
            id_count += 1
    return (id_count / len(alignment_list[0]) * 100)


def abundance_greedy_clustering(amplicon_file: Path, minseqlen: int, mincount: int, chunk_size: int, kmer_size: int) -> List:
    """Compute an abundance greedy clustering regarding sequence count and identity.
    Identify OTU sequences.

    :param amplicon_file: (Path) Path to the amplicon file in FASTA.gz format.
    :param minseqlen: (int) Minimum amplicon sequence length.
    :param mincount: (int) Minimum amplicon count.
    :param chunk_size: (int) A fournir mais non utilise cette annee
    :param kmer_size: (int) A fournir mais non utilise cette annee
    :return: (list) A list of all the [OTU (str), count (int)] .
    """

    print("working until here 0")
    # Get the dereplicated sequences
    dereplicated_seq = dereplication_fulllength(
        amplicon_file,
        minseqlen,
        mincount
        )

    # Create the alignment bewteen the sequence and the OTUs
    i = 0
    # print("working until here")
    for seq, count in dereplicated_seq:
        print("i", i)
        print("i", i, "seq", seq, "count", count)
        # Initialize the OTU list
        if i == 0:
            OTU_list = [[seq, count]]
        else:
            # Compare the sequence with the OTU list
            to_add = True
            for otu in OTU_list:
                if seq != otu[0]:
                    alignment = nw.global_align(
                        seq,
                        otu[0],
                        gap_open=-1,
                        gap_extend=-1,
                        matrix=str(Path(__file__).parent / "MATCH"))
                    print("--------------------- alignment ---------------------")
                    print(alignment)

                    # Compute the identity
                    identity = get_identity(alignment)
                    print("identity", identity)
                    print("sequence occurency", count)
                    print("otu occurency", otu[1])
                    # Check if the identity is greater than 97%
                    if identity >= 97:
                        to_add = False
                        break
            # Add the sequence to the OTU list if it is not already in
            if to_add:
                OTU_list.append([seq, count])
        i += 1
        print(" --------------------- OTU_list ---------------------")
        for otu in OTU_list:
            print(otu)
    return OTU_list



def write_OTU(OTU_list: List, output_file: Path) -> None:
    """Write the OTU sequence in fasta format.

    :param OTU_list: (list) A list of OTU sequences
    :param output_file: (Path) Path to the output file
    """

    with open(output_file, 'w') as f:
        for index, (sequence, count) in enumerate(OTU_list, start=1):
            # Write header
            f.write(f">OTU_{index} occurrence:{count}\n")
            # Write sequence
            wrapped_sequence = textwrap.fill(sequence, width=80)
            f.write(f"{wrapped_sequence}\n")


#==============================================================
# Main program
#==============================================================
def main(): # pragma: no cover
    """
    Main program function
    """
    # Get arguments
    args = get_arguments()
    
    # Compute the OTU
    otu_list = abundance_greedy_clustering(
        args.amplicon_file,
        args.minseqlen,
        args.mincount,
        1000,
        8
    )
    # Write the output
    write_OTU(otu_list, args.output_file)



if __name__ == '__main__':
    main()
