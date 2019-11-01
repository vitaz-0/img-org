from pathlib import Path
import os
import click
import csv
from shutil import copy

# @imgorg.command()
# @click.argument('src_dir', required=True)
# @click.argument('tgt_dir', required=True)
# @click.argument('ref_file', required=True)
src_dir = "/Users/vitek/Pictures/2018_Nepal_India/INDIA/jpeg"
tgt_dir = "/Users/vitek/Pictures/2018_Nepal_India/INDIA/vyber_Indie"
ref_file = "/Users/vitek/Pictures/albums_list/Nepal_India/INDIA/vyber_india"
def cp(src_dir, tgt_dir, ref_file):

    with open(ref_file, 'r') as csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            src_file = os.path.join(src_dir,row[0])
            tgt_file = os.path.join(tgt_dir,row[0])
            print("copying: ", src_file)
            copy(src_file, tgt_file)

cp(src_dir, tgt_dir, ref_file)
