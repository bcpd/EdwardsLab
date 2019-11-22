"""
Parse a GTO object
"""

import os
import sys
import argparse

from roblib import bcolors
import json


def list_keys(gto, verbose=False):
    """
    List the primary keys in the patric file
    :param gto: the json gto
    :param verbose: more output
    :return:
    """
    print("{}".format("\n".join(gto.keys())))

def dump_json(gto, k, verbose=False):
    """
    Print out the json representation of some data
    :param gto: the json gto
    :param k: the key to dump (none for everything)
    :param verbose: more output
    :return:
    """

    if k:
        if k in gto:
            print(json.dumps(gto[k], indent=4))
        else:
            sys.stderr.write(f"{bcolors.RED}ERROR: {k} not found.{bcolors.ENDC}\n")
    else:
        print(json.dumps(gto, indent=4))

def feature_tbl(gto, verbose=False):
    """
    Print a tab separated feature table
    :param gto: the json gto
    :param verbose: more output
    :return:
    """

    for peg in gto['features']:
        if 'location' not in peg:
            sys.stderr.write(f"{bcolors.RED}Error: no location found\n{bcolors.PINK}{peg}{bcolors.ENDC}\n")
            continue

        locs = []
        for l in peg['location']:
            start = int(l[1])
            if l[2] == '+':
                stop = (start + int(l[3])) - 1
            elif l[2] == '-':
                start  = (start - int(l[3])) + 1
                stop = int(l[1])
            else:
                sys.stderr.write(f"{bcolors.RED}Error: Don't know location l[2]\n{bcolors.ENDC}")
                continue
            locs.append(f"{l[0]} {start} - {stop} ({l[2]})")

        data = [
            peg['id'],
            peg['function'],
            "; ".join(locs)
        ]
        print("\t".join(data))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Plot a heatmap")
    parser.add_argument('-f', help='gto file', required=True)
    parser.add_argument('-l', help='list the primary keys and exit', action='store_true')
    parser.add_argument('-d', help='dump some part of the json object', action='store_true')
    parser.add_argument('-p', help='print protein feature table', action='store_true')
    parser.add_argument('-k', help='json primary key (e.g. for dumping, etc)')
    parser.add_argument('-o', help='output file')
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    gto = json.load(open(args.f, 'r'))

    if args.l:
        list_keys(gto, args.v)
        sys.exit(0)

    if args.d:
        dump_json(gto, args.k, args.v)
        sys.exit(0)

    if args.p:
        feature_tbl(gto, args.v)
        sys.exit(0)

    sys.stderr.write(f"{bcolors.RED}ERROR: You did not specify a command to run{bcolors.ENDC}\n")
