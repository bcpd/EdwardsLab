"""
Make a table for Tom Jeffries from the data we computed for him
"""

import os
import sys
import argparse
from roblib import message

__author__ = 'Rob Edwards'
__copyright__ = 'Copyright 2020, Rob Edwards'
__credits__ = ['Rob Edwards']
__license__ = 'MIT'
__maintainer__ = 'Rob Edwards'
__email__ = 'raedwards@gmail.com'

def crassphage_coverage(f, verbose=False):
    """
    Get the crassphage coverage. This is coverage.txt
    :param f: coverage.txt
    :param verbose: more output
    :return:
    """

    coverage = {}

    if verbose:
        message(f"Reading {f}", "GREEN")

    with open(f, 'r') as fin:
        for l in fin:
            p = l.strip().split("\t")
            coverage[p[0]] = int(p[1]) / 97092

    return coverage


def abricate_counts(data_directory, verbose=False):
    """ find the abricate folders and read them """

    count = {}
    allabr = set()
    for sample in os.listdir(data_directory):
        if verbose:
            message(f"Abricate: {sample}", "PINK")
        count[sample] = {}
        if os.path.exists(os.path.join(data_directory, sample, "abricate")):
            for f in os.listdir(os.path.join(data_directory, sample, "abricate")):
                if f.endswith('.tab'):
                    with open(os.path.join(data_directory, sample, "abricate", f), 'r') as fin:
                        for l in fin:
                            p = l.strip().split("\t")
                            abr = f"{p[11]}:{p[5]}"
                            count[sample][abr] = count[sample].get(abr, 0) + 1
                            allabr.add(abr)
    return count, allabr


def focus_counts(data_directory, verbose=False):
    """ find the focus output and read it"""
    count = {}
    allfocus = set()
    for sample in os.listdir(data_directory):
        if verbose:
            message(f"Focus: {sample}", "BLUE")
        count[sample] = {}
        if os.path.exists(os.path.join(data_directory, sample, "focus", "output_All_levels.csv")):
            with open(os.path.join(data_directory, sample, "focus", "output_All_levels.csv"), 'r') as fin:
                lastcol = -1
                for l in fin:
                    if l.startswith('Kingdom'):
                        if 'pass_1.fasta'in l and 'pass_2.fasta' in l:
                            lastcol = -2
                        continue
                    l = l.strip()
                    tax = ":".join(l.split(",")[0:lastcol])
                    # note that even if we split the tax to the previous column
                    # we use R2 for the reads then it is consistent with the sf output :)
                    count[sample][tax] = l.split(",")[-1]
                    allfocus.add(tax)
    return count, allfocus

def superfocus_counts(data_directory, level=3, verbose=False):
    """
    find the superfocus output and read it. The file name loooks like
    data/DRR042358/sf/DRR042358all_levels_and function.xls
    :param data_directory: data/
    :param level: the ss level. Currently only 1, 2, and 3 are supported. 2 is 1+2
    :param verbose: more output
    :return:
    """

    count = {}
    allsslvl = set()

    for sample in os.listdir(data_directory):
        if verbose:
            message(f"Super focus: {sample}", "YELLOW")
        count[sample] = {}
        sffile = os.path.join(data_directory, sample, "sf", f"{sample}all_levels_and_function.xls")
        if os.path.exists(sffile):
            keep = False
            with open(sffile, 'r') as fin:
                for l in fin:
                    if l.startswith('Subsystem Level 1'):
                        keep = True
                        continue
                    if not keep:
                        continue
                    p = l.strip().split("\t")
                    if level == 1:
                        sslvl = [0]
                    elif level == 2:
                        sslvl = ":".join([p[0], p[1]])
                    else:
                        sslvl = p[2]
                    count[sample][sslvl] = count[sample].get(sslvl, 0) + float(p[-1])
                    allsslvl.add(sslvl)
    return count, allsslvl

def write_file(samples, counts, allkeys, file, verbose=False):
    """ Write the appropriate output files"""

    ak = sorted(list(allkeys))

    if verbose:
        message(f"Writing to {file}", "GREEN")

    with open(file, 'w') as out:
        out.write("\t".join(["Sample"] + ak))
        out.write("\n")
        for s in samples:
            out.write(s)
            for k in ak:
                if k in counts[s]:
                    out.write(f"\t{counts[s][k]}")
                else:
                    out.write("\t0")
            out.write("\n")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=" ")
    parser.add_argument('-c', help='coverage file', required=True)
    parser.add_argument('-d', help='data directory', required=True)
    parser.add_argument('-o', help='output file base name. Stuff will be appended to this', required=True)
    parser.add_argument('-l', help='subsystem level (1,2, or 3) (default = 3)', type=int, default=3)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    if args.l < 1 or args.l > 3:
        message(f"Error: No subsystem level {args.l}. Defaulting to 3", "RED")
        args.l = 3

    coverage = crassphage_coverage(args.c, args.v)
    abricate, allabricate = abricate_counts(args.d, args.v)
    focus, allfocus = focus_counts(args.d, args.v)
    sf, allsf = superfocus_counts(args.d, args.l, args.v)

    # now get all the samples that are in abricate, focus, or sf
    samples = set(abricate.keys())
    samples.update(focus.keys())
    samples.update(sf.keys())

    sortedsamples = sorted(samples)

    # now print everything out!
    # lets do this as separate files and then we can join them after

    if args.v:
        message("Writing coverage", "GREEN")

    with open(f"{args.o}.coverage.tsv", 'w') as out:
        out.write("Sample\tCoverage\n")
        for k in sortedsamples:
            out.write(f"{k}\t{coverage[k]}\n")

    write_file(sortedsamples, abricate, allabricate, f"{args.o}.abricate.tsv", args.v)
    write_file(sortedsamples, focus, allfocus, f"{args.o}.focus.tsv", args.v)
    write_file(sortedsamples, sf, allsf, f"{args.o}.superfocus.tsv", args.v)
