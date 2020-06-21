"""
Convert a genbank file to sequences
"""

import os
import sys
import argparse
from roblib import genbank_to_faa, genbank_to_fna, genbank_to_orfs

__author__ = 'Rob Edwards'
__copyright__ = 'Copyright 2020, Rob Edwards'
__credits__ = ['Rob Edwards']
__license__ = 'MIT'
__maintainer__ = 'Rob Edwards'
__email__ = 'raedwards@gmail.com'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=" ")
    parser.add_argument('-g', '--genbank', help='genbank file', required=True)
    parser.add_argument('-c', '--complex', help='complex identifier line', action='store_true')
    parser.add_argument('-a', '--aminoacids', help="output file for the amino acid sequences")
    parser.add_argument('-n', '--nucleotide', help='output file for nucleotide sequence')
    parser.add_argument('-o', '--orfs', help='output file for orfs')
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    did = False
    if args.nucleotide:
        with open(args.nucleotide, 'w') as out:
            for sid, seq in genbank_to_fna(args.genbank):
                out.write(f">{sid}\n{seq}\n")
        did = True

    if args.aminoacids:
        with open(args.aminoacids, 'w') as out:
            for sid, seq in genbank_to_faa(args.genbank, args.complex), args.v:
                out.write(f">{sid}\n{seq}\n")
        did = True

    if args.orfs:
        with open(args.orfs, 'w') as out:
            for sid, seq in genbank_to_orfs(args.genbank, args.complex), args.v:
                out.write(f">{sid}\n{seq}\n")
        did = True

    if not did:
        sys.stderr.write("Please provide either a -n or -a output file! (or both)")


