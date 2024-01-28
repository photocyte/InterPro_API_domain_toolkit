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
python InterPro_API_fetch_domain_aware_FASTA.py IPR036188 7227

INPUT_FASTA=./downloads/uniprot_IPR036188_7227.fasta

echo "!! RUNNING InterPro_FASTA_description_to_bed.py !!"
./InterPro_FASTA_description_to_bed.py ${INPUT_FASTA}

echo "!! RUNNING bedtools !!"
mkdir -p bed_fasta
for b in ./bed/*
do
bedtools getfasta -name -fi $INPUT_FASTA -bed $b > bed_fasta/$(basename $b).fasta

done

echo "(All done!, check for the results in the downloads, bed, and bed_fasta folders...)"
