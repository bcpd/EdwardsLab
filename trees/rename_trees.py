import os
import sys
import argparse
import os
import string
import sys
from roblib import Newick_Tree

__author__ = 'Rob Edwards'

"""
Rename tree leaves and print out the tree
"""




def clean_name(self, name):
    """
    Just clean out non-allowable characters in the name

    :param name: the new name
    :type name: str
    :return: the revised name
    :rtype: str
    """

    allowable = set(string.ascii_letters)
    allowable.update(set(string.digits))
    allowable.update({'_','-',':'})
    name.replace(' ', '_')
    return filter(lambda x: x in allowable, name)

def rename_nodes(self, node, idmap):
    """
    Rename the nodes of a tree based on id map

    :param root: the root node of the tree
    :type root: Node
    :param idmap: the id map
    :type idmap: dict
    :return: the new root node
    :rtype: Node
    """

    if node.name and node.name in idmap:
        node.name = clean_name(idmap[node.name])
    if node.left:
        node.left = rename_nodes(node.left, idmap)
    if node.right:
        node.right = rename_nodes(node.right, idmap)

    return node


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse a tree')
    parser.add_argument('-t', help='tree file', required=True)
    parser.add_argument('-i', help='id map file', required=True)
    args = parser.parse_args()

    idmap = {}
    with open(args.i, 'r') as f:
        for l in f:
            p=l.strip().split("\t")
            idmap[p[0]]=p[1].split()[0]


    tre = []
    with open(args.t, 'r') as f:
        for l in f:
            tre.append(l.strip())

    root = Newick_Tree().parse(''.join(tre))
    root = rename_nodes(root, idmap)
    Newick_Tree().print_tree(root)

