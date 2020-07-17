"""
Read a genbank file and do things with it!
"""

import os
import sys
import re
import binascii
import gzip
from Bio import SeqIO


__author__ = 'Rob Edwards'
__copyright__ = 'Copyright 2020, Rob Edwards'
__credits__ = ['Rob Edwards']
__license__ = 'MIT'
__maintainer__ = 'Rob Edwards'
__email__ = 'raedwards@gmail.com'


def is_gzip(gbkf):
    """
    Is the file compressed?
    :param gbkf:
    :return: true if compressed else false
    """

    with open(gbkf, 'rb') as i:
        return binascii.hexlify(i.read(2)) == b'1f8b'


def genbank_seqio(gbkf, verbose=False):
    """
    Get the parser stream
    :param gbkf: genbank file
    :param verbose:
    :return:
    """

    if is_gzip(gbkf):
        handle = gzip.open(gbkf, 'rt')
    else:
        handle = open(gbkf, 'r')
    return SeqIO.parse(handle, "genbank")

def feature_id(seq, feat):
    """
    Choose the appropriate id for the feature
    :param feat: the feature
    :return: the id
    """

    if 'protein_id' in feat.qualifiers:
        return '|'.join(feat.qualifiers['protein_id'])
    elif 'locus_tag' in feat.qualifiers:
        return "|".join(feat.qualifiers['locus_tag'])
    elif 'db_xref' in feat.qualifiers:
        return '|'.join(feat.qualifiers['db_xref'])
    else:
        return seq.id + "." + str(feat.location)

def feat_to_text(feat, qual):
    if qual in feat.qualifiers:
        return " ".join(feat.qualifiers[qual])
    return "-"

def genbank_to_fna(gbkf):
    """
    Parse a genbank file
    :param gbkf: genbank file
    :param verbose:
    :return: a dict of the sequences
    """

    for seq in genbank_seqio(gbkf):
        yield seq.id, seq.seq

def genbank_to_faa(gbkf, complexheader=False, verbose=False):
    """
    Parse a genbank file
    :param gbkf: the genbank file
    :param complexheader: more detail in the header
    :param verbose: more output
    :return: yield the protein id and sequence
    """

    for seq in genbank_seqio(gbkf):
        for feat in seq.features:
            if feat.type != 'CDS':
                continue
            (start, stop, strand) = (feat.location.start.position, feat.location.end.position, feat.strand)
            prtmtd = {
                'EC_number': "",
                'locus_tag': "",
                'note': "",
                'product': "",
                'protein_id': "",
                'ribosomal_slippage': "",
                'transl_table': 11,
                'translation': ""
            }

            cid = feature_id(seq, feat)

            if complexheader:
                loc = f"{start}_{stop}"
                if strand < 0:
                    loc = f"{stop}_{start}"

                cid += f' [{seq.id}] '
                if 'organism' in seq.annotations:
                    cid += f' [{seq.annotations["organism"]}]'
                cid += f' [{seq.id}_{loc}]'
                if 'product' in feat.qualifiers:
                    cid += f' {feat.qualifiers["product"][0]}'
                else:
                    cid += f' [hypothetical protein]'

            if 'translation' in feat.qualifiers:
                yield seq.id, cid, feat.qualifiers['translation'][0]
            else:
                yield seq.id, cid, str(feat.extract(seq).translate().seq)


def genbank_to_functions(gbkf, verbose=False):
    """
    Parse a genbank file
    :param gbkf: the genbank file
    :param verbose: more output
    :return: yield a tple of [protein id, function]
    """
    for seq in genbank_seqio(gbkf):
        for feat in seq.features:
            if feat.type != 'CDS':
                continue

            cid = feature_id(seq, feat)

            prod = "Hypothetical protein"
            if "product" in feat.qualifiers:
                prod = "|".join(feat.qualifiers['product'])

            yield cid, prod


def genbank_to_orfs(gbkf, complexheader=False, verbose=False):
    """
    Parse a genbank file
    :param gbkf:
    :param complexheader:
    :param verbose:
    :return: a dict of the sequences
    """

    for seq in genbank_seqio(gbkf):
        for feat in seq.features:
            if feat.type != 'CDS':
                continue
            (start, stop, strand) = (feat.location.start.position, feat.location.end.position, feat.strand)
            prtmtd = {
                'EC_number': "",
                'locus_tag': "",
                'note': "",
                'product': "",
                'protein_id': "",
                'ribosomal_slippage': "",
                'transl_table': 11,
                'translation': ""
            }

            cid = feature_id(seq, feat)

            if complexheader:
                loc = f"{start}_{stop}"
                if strand < 0:
                    loc = f"{stop}_{start}"

                cid += f' [{seq.id}] '
                if 'organism' in seq.annotations:
                    cid += f' [{seq.annotations["organism"]}]'
                cid += f' [{seq.id}_{loc}]'
                if 'product' in feat.qualifiers:
                    cid += f' {feat.qualifiers["product"][0]}'
                else:
                    cid += f' [hypothetical protein]'

            yield seq.id, cid, str(feat.extract(seq).seq)


def genbank_to_ptt(gbkf, printout=False, verbose=False):
    """
    Convert the genbank file to a table with the same columns of the ptt file
    :param gbkf: the genbank input file
    :param printout: print the table
    :param verbose: more output
    :return: the table
    """

    res = []

    gire = re.compile('GI:(\d+)')
    cogre = re.compile('(COG\S+)')
    for seq in genbank_seqio(gbkf):
        if verbose:
            sys.stderr.write(f"Parsing {seq.id}\n")
        for feat in seq.features:
            if feat.type != "CDS":
                continue

            gi = "-"
            if gire.match(feat_to_text(feat, 'db_xref')):
                gi = gire.match(feat_to_text(feat, 'db_xref'))[1]

            cog = "-"
            if cogre.match(feat_to_text(feat, 'product')):
                cog = cogre.match(feat_to_text(feat, 'product'))[1]

            gene = feat_to_text(feat, 'gene')
            if gene == "-":
                gene = str(feat.location)

            cid = feature_id(seq, feat)

            thisres = [
                f"{feat.location.start}..{feat.location.end}",
                "+" if feat.strand >= 0 else "-",
                (len(feat.location) / 3) - 1,
                gi,
                gene,
                cid,
                cog,
                feat_to_text(feat, 'product')
            ]

            if printout:
                print("\t".join(map(str, thisres)))

            res.append(thisres)

    return res

def genbank_to_phage_finder(gbkf, verbose=False):
    """
    This is a very specific format used by phage_finder (http://phage-finder.sourceforge.net/documentation.htm)
    - contig id, including >
    - length of the contig
    - gene ID
    - start
    - end
    - function

    :param gbkf: the genbank file
    :param verbose: more output
    :return: yields a tple of this data
    """

    for seq in genbank_seqio(gbkf):
        for feat in seq.features:
            if feat.type != 'CDS':
                continue
            cid = feature_id(seq, feat)
            fn = "Hypothetical protein"
            if 'product' in feat.qualifiers:
                fn = feat_to_text(feat, 'product')
            yield [seq.id, len(seq.seq), cid, feat.location.start, feat.location.end, fn]

