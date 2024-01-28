#!/usr/bin/env python3

## This python file, takes a reviewed_G3DSA3.10.129.110_1836.fasta type file, and extracts the relevant regions that define the domains, outputting a bed file.
import argparse
import re
import os
import pandas as pd
from pathvalidate import is_valid_filename, sanitize_filename

parser = argparse.ArgumentParser(description='Python script to convert InterPro fasta description to bed regions')

parser.add_argument('IPR_API_FASTA_path', type=str, metavar='<IPR_API_FASTA>', help='InterPro API sourced FASTA with IPR domains annotated in the FASTA record descriptions')
parser.add_argument('-o','--output_folder', type=str, metavar='<OUTPUT_FOLDER>', help='Default output folder for the bed files. Default="bed"', default='bed')
parser.add_argument('-r','--rename', type=str, metavar='<yes OR no>', help='Activate PKS domain remaining. Affects Name column. Default="no"', default='no')

args = parser.parse_args()

if args.rename == "yes":
    rename_df = pd.read_csv('zenodo_items/doi--10.5281--zenodo.10023460/interproscan_plot/run2_filter.tsv', sep='\t', header=0, index_col=None)
    rename_dict = dict(zip(rename_df['InterProScan_annotated_region'], rename_df['Short_PKS_nomenclature']))

def InterPro_FASTA_description_to_bed(filepath):
    ## This was originally intended to run off the `seqkit fx2tab -n` produced TSV file.
    ## Have since adapted it to use the InterPro API FASTA directly. 
    handle = open(filepath, 'r')
    lines = handle.readlines()
    handle.close()

    ##equivalent to mkdir -p
    try:
        os.mkdir(args.output_folder)
    except  FileExistsError:
        pass

    for l in lines:
        if not l.startswith('>'):
            continue
        l = l.strip('>').strip()

        seq_id = re.findall(r'^[^\s]+', l)[0]
        ipr_re = re.compile(f'{seq_id}\s+([^(]+)')
        IPR_id = re.search(ipr_re, l).group(1)
        #print(IPR_id)
        #print(l)
        regions = re.findall(r'\([0-9]+[^)]+...[0-9]+\)', l)[0]

        regions = re.split(',|;',regions) ## I don't know why sometimes the delimiter changes from a semicolon to comma
        #print(regions)

        if type(regions) == str:
            regions = [ regions ]

        regions = [ r.strip('(').strip(')') for r in regions ]
        regions = [ r.split('...') for r in regions ]

        #print(regions)


        
            

        output_filename = f'{args.output_folder}/{seq_id}_{sanitize_filename(IPR_id)}.bed'
        with open(output_filename, 'w') as f:
            domain_index = 1
            for r in regions:
                if args.rename == 'yes':
                    IPR_id_r = rename_dict[IPR_id]+str(domain_index)
                    domain_index += 1 
                else:
                    IPR_id_r = IPR_id
                bed_line = '\t'.join([seq_id, str(int(r[0])-1), str(int(r[1])-1),IPR_id_r])+'\n' ## -1 to match with 0-indexed bed format
                f.write(bed_line) 

InterPro_FASTA_description_to_bed(args.IPR_API_FASTA_path)
