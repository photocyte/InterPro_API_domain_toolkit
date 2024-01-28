#!/usr/bin/env python3
import argparse
import re
import urllib
import urllib.request
import time
import os
import glob
import rdflib ## conda install -c conda-forge rdflib

parser = argparse.ArgumentParser(description='Python script to make a key-value renaming file from a Uniprot RDF.XML entry metadata.')

files = glob.glob('rdf/*rdf.xml')

for f in files:
    #print(f)
    g = rdflib.Graph()
    g.parse(f, format='xml')

    # Loop through each triple in the graph (subj, pred, obj)
    for subj, pred, obj in g:
        if 'mnemonic' in pred:
            #print('WOOP')
            #print(subj, pred, obj)
            Uniprot_id = subj.split('/')[-1]
            print('\t'.join([Uniprot_id,obj]))
        
        # Check if there is at least one triple in the Graph
        if (subj, pred, obj) not in g:
            raise Exception("It better be!")

    # Print the number of "triples" in the Graph
    #print(f"Graph g has {len(g)} statements.")
    # Prints: Graph g has 86 statements.

    # Print out the entire Graph in the RDF Turtle format
    #print(g.serialize(format="turtle"))
