#!/usr/bin/env python3
import argparse
import re
import urllib
import urllib.request
import time
import os

parser = argparse.ArgumentParser(description='Python script to fetch RDF metadata from InterPro fasta descriptions')

parser.add_argument('IPR_API_FASTA_path', type=str, metavar='<IPR_API_FASTA>', help='InterPro API sourced FASTA with IPR domains annotated in the FASTA record descriptions')
parser.add_argument('-o','--output_folder', type=str, metavar='<OUTPUT_FOLDER>', help='Default output folder for the RDF files. Default="rdf"', default='rdf')
args = parser.parse_args()

def InterPro_FASTA_description_to_RDF(filepath):
    ## This was originally intended to run off the `seqkit fx2tab -n` produced TSV file.
    ## Have since adapted it to use FASTA directly. 
    handle = open(filepath, 'r')
    lines = handle.readlines()
    handle.close()

    for l in lines:
        if not l.startswith('>'):
            continue
        l = l.strip('>').strip()
        seq_id = re.findall(r'^[^\t]+', l)[0]
        BASE_URL=f'https://rest.uniprot.org/uniprotkb/{seq_id}?format=rdf'
        
        ##equivalent to mkdir -p
        try:
            os.mkdir(args.output_folder)
        except  FileExistsError:
            pass

        output_filename = f'{args.output_folder}/{seq_id}.rdf.xml'

        if os.path.exists(output_filename):
            print(f'{output_filename} already exists. Skipping...')
            continue

        result = urllib.request.urlopen(BASE_URL)

        with open(output_filename, 'w') as f:
            f.write(result.read().decode('utf-8'))

        time.sleep(1)

InterPro_FASTA_description_to_RDF(args.IPR_API_FASTA_path)
