"""
Read one or more protein fasta files and calculate md5sums
"""

import os
import sys
import argparse
import hashlib
from roblib import stream_fasta, bcolors

def read_fasta(fafile, idmapfile, verbose=False):
    """
    Read a fasta file and return a dict of proteins and their md5 sums
    :param fafile: fasta file
    :param verbose: more output
    :return:
    """

    if verbose:
        sys.stderr.write(f"{bcolors.GREEN}Reading {fafile}{bcolors.ENDC}\n")

    seqs = {}
    with open(idmapfile, 'a') as out:
        for seqid, seq in stream_fasta(fafile):
            md5 = hashlib.md5(seq.upper().encode('utf-8')).hexdigest()
            seqs[md5] = seq
            out.write(f"{md5}\t{seqid}\n")

    return seqs





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=" ")
    parser.add_argument('-f', help='file')
    parser.add_argument('-d', help='directory of fasta files')
    parser.add_argument('-i', help='id map file to write')
    parser.add_argument('-o', help='output file')
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    seqs = {}
    if args.f:
        seqs.update(read_fasta(args.f, args.i, args.v))

    if args.d:
        for f in os.listdir(args.d):
            seqs.update(read_fasta(os.path.join(args.d, f), args.i, args.v))

    with open(args.o, 'w') as out:
        for m in seqs:
            out.write(f">{m}\n{seqs[m]}\n")
