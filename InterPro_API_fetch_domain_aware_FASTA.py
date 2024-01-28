#!/usr/bin/env python3

## This script was downloaded from here: https://www.ebi.ac.uk/interpro/result/download/#/protein/UniProt/entry/InterPro/IPR036736/taxonomy/uniprot/2830/|fasta:~:text=Download%20script%20file
## And modified from there to use argparse parameters

# standard library modules
import sys, errno, re, json, ssl
from urllib import request
from urllib.error import HTTPError
import urllib
from time import sleep
import argparse
from pathvalidate import is_valid_filename, sanitize_filename
import os

parser = argparse.ArgumentParser(description='InterPro API script to download FASTA files for a given InterPro domain and taxonomy ID')
    
# Define the two required positional arguments
parser.add_argument('InterPro_ID', type=str, metavar='<InterPro_ID>', help='InterPro Domain ID to search for, i.e. IPR036736 for ACP domains')
parser.add_argument('Taxonomy_Filter', type=str, metavar='<Taxonomy_ID>', help='Taxonomy ID to filter by, i.e. 2830 for haptophyte algae, or 2 for bacteria')

# Define the optional arguments, where a reasonable default can be set
parser.add_argument('-d','--db', type=str, metavar='<database_to_use>', help='Database to search against, either "uniprot" or "reviewed" (aka Swiss-Prot). Default is "uniprot"', default="uniprot")
parser.add_argument('-o','--output_file', type=str, metavar='<output_filename>', help='Output filename, defaults to <database_to_use>_<InterPro_ID>_<Taxonomy_ID>.fasta', default=None)
parser.add_argument('-f','--output_folder', type=str, metavar='<prefix_dir>', help='Prefix directory for outputs, defaults to "downloads"', default="downloads")

args = parser.parse_args()

if args.db == "uniprot":
  db_var = "UniProt"
elif args.db == "reviewed":
  db_var = "reviewed"
else:
  sys.stderr.write("Database must be either 'uniprot' or 'reviewed'")
  sys.exit(1)

if args.InterPro_ID.startswith("IPR"):
  ##Integrated InterPro entry
  BASE_URL = f'https://www.ebi.ac.uk:443/interpro/api/protein/{db_var}/entry/InterPro/{args.InterPro_ID}/taxonomy/uniprot/{args.Taxonomy_Filter}/?page_size=200&extra_fields=sequence'
elif args.InterPro_ID.startswith("G3DSA"):
  ##CATH-Gene3D entry
  BASE_URL = f'https://www.ebi.ac.uk:443/interpro/api/protein/{db_var}/entry/all/cathgene3d/{args.InterPro_ID}/taxonomy/uniprot/{args.Taxonomy_Filter}/?page_size=200&extra_fields=sequence'
elif args.InterPro_ID.startswith("SSF"):
  ##SUPERFAMILY entry
  pass
  sys.stderr.write("Not yet implemented. Exiting.\n")
  sys.exit(1)
elif args.InterPro_ID.startswith("PF"):
  ##Pfam entry
  pass
  sys.stderr.write("Not yet implemented. Exiting.\n")
  sys.exit(1)
else:
  sys.stderr.write("InterPro ID seems invalid. Are you sure it is structured correctly?'")
  sys.exit(1)

HEADER_SEPARATOR = "\t"
LINE_LENGTH = 80

sys.stderr.write("Initial parameter checks passed.\n")
sys.stderr.write('''Now querying the InterPro API. Please don't abuse InterPro's computational resources by making ridiculously large queries!\n''')

def output_list():
  #disable SSL verification to avoid config issues
  context = ssl._create_unverified_context()

  next = BASE_URL
  last_page = False

  sys.stderr.write(f'Downloading FASTA file for InterPro ID {args.InterPro_ID} and Taxonomy ID {args.Taxonomy_Filter} from database {args.db}\n')
  sys.stderr.write(f'BASE_URL is {BASE_URL}\n')

          ##equivalent to mkdir -p
  try:
    os.mkdir(args.output_folder)
  except  FileExistsError:
    pass

  if args.output_file == None:
    ## recommend using the pathvalidate library if filenames need to be sanitized
    output_filename = f'{args.db}_{args.InterPro_ID}_{args.Taxonomy_Filter}.fasta'
    output_filename = sanitize_filename(output_filename)
    output_filename = f'{args.output_folder}/{output_filename}'
  else:
    output_filename = f'{args.output_folder}/{args.output_file}'

  if os.path.isfile(output_filename):
    sys.stderr.write(f'Output file {output_filename} already exists, assuming as cache. Please delete it if you want to download it freshly again\n')
    sys.stderr.write("Exiting.\n")
    sys.exit(1)

  output_tmp_filename = os.path.join(args.output_folder,'tmp__'+os.path.basename(output_filename))
  output_handle = open(output_tmp_filename, "w")
  
  attempts = 0
  while next:
    try:
      req = request.Request(next, headers={"Accept": "application/json"})
      res = request.urlopen(req, context=context)
      # If the API times out due a long running query
      if res.status == 408:
        # wait just over a minute
        sleep(61)
        # then continue this loop with the same URL
        continue
      elif res.status == 204:
        #no data so leave loop
        break
      payload = json.loads(res.read().decode())
      next = payload["next"]
      attempts = 0
      if not next:
        last_page = True
    except HTTPError as e:
      if e.code == 408:
        sleep(61)
        continue
      else:
        # If there is a different HTTP error, it wil re-try 3 times before failing
        if attempts < 3:
          attempts += 1
          sleep(61)
          continue
        else:
          sys.stderr.write("LAST URL: " + next)
          raise e

    for i, item in enumerate(payload["results"]):
      
      entries = None
      if ("entry_subset" in item):
        entries = item["entry_subset"]
      elif ("entries" in item):
        entries = item["entries"]
      
      if entries is not None:
        entries_header = "-".join(
          [entry["accession"] + "(" + ";".join(
            [
              ",".join(
                [ str(fragment["start"]) + "..." + str(fragment["end"]) 
                  for fragment in locations["fragments"]]
              ) for locations in entry["entry_protein_locations"]
            ]
          ) + ")" for entry in entries]
        )
        output_handle.write(">" + item["metadata"]["accession"] + HEADER_SEPARATOR
                          + entries_header + HEADER_SEPARATOR
                          + item["metadata"]["name"] + "\n")
      else:
        output_handle.write(">" + item["metadata"]["accession"] + HEADER_SEPARATOR + item["metadata"]["name"] + "\n")

      seq = item["extra_fields"]["sequence"]
      fastaSeqFragments = [seq[0+i:LINE_LENGTH+i] for i in range(0, len(seq), LINE_LENGTH)]
      for fastaSeqFragment in fastaSeqFragments:
       output_handle.write(fastaSeqFragment + "\n")
      
    # Don't overload the server, give it time before asking for more
    if next:
      sleep(1)
  output_handle.close()
  os.rename(output_tmp_filename, output_filename) ## To ensure incomplete files don't get written.

if __name__ == "__main__":
  output_list()
