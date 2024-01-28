#! /bin/bash

## Search here to get the taxonomy ID for your organism of interest:
## https://www.uniprot.org/taxonomy?query=*
## Here's an example:
## https://www.uniprot.org/taxonomy/7227 ## The fruit fly Drosoophila melanogaster

## For the InterPro ID, ideally you'd have picked an InterPro matcher that gives
## a lot of sensitivity and specificity for your question of interest
## (this is not always the case, I've run into cases of cross-matches, and generally just
## confusion, so do your due dilligence to be sure whatever the source database the InterPRo
## ID is sourced from, is actually answering the question you think it is!)
## Here's an example:
## https://www.ebi.ac.uk/interpro/search/text/IPR036188/?page=1#table

## Fetch all the proteins from D. melanogaster that contain IPR036188 (one superfamily of known flavoprotein) domains
echo "!! RUNNING InterPro_API_fetch_domain_aware_FASTA.py !!"
python InterPro_API_fetch_domain_aware_FASTA.py -f example_downloads IPR036188 7227

INPUT_FASTA=./example_downloads/uniprot_IPR036188_7227.fasta

echo "!! RUNNING InterPro_FASTA_description_to_bed.py !!"
FASTA_TO_BED_OUTPUT_DIR=example_bed
./InterPro_FASTA_description_to_bed.py -o ${FASTA_TO_BED_OUTPUT_DIR} ${INPUT_FASTA}

BEDTOOLS_OUTPUT_DIR="example_bed_fasta"
echo "!! RUNNING bedtools !!"
mkdir -p ${BEDTOOLS_OUTPUT_DIR}
for b in ./${FASTA_TO_BED_OUTPUT_DIR}/*
do
bedtools getfasta -name -fi $INPUT_FASTA -bed $b > "${BEDTOOLS_OUTPUT_DIR}/$(basename $b).fasta"
done

echo "(All done!, check for the results in the downloads, bed, and bed_fasta folders...)"
