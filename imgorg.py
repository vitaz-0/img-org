from subprocess import Popen, PIPE
from pathlib import Path
import click
import os

def ls(directory):
    ls = Popen(["ls", "-p", directory], stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    grep = Popen(["grep", "-v", "/$"],stdin=ls.stdout,stdout=PIPE)
    endOfPipe = grep.stdout

    files = []
    for line in endOfPipe:
        files.append(line.strip().decode('utf-8'))

    return files

def listPhotos():
    scpt = '''
        tell application "Photos"
            --activate
            try
                set photosSelection to selection
                    if photosSelection is {} then error "The selection  is empty" -- no selection
                on error errTexttwo number errNumtwo
                    display dialog "No photos selected " & errNumtwo & return & errTexttwo
                    return
            end try

            set allPhotos to {}

            repeat with aPhoto in photosSelection
                set the photoProps to the properties of aPhoto
                set photoName to filename of photoProps
                --log "Photo: " & filename of photoProps
                copy filename of photoProps to the end of the allPhotos
            end repeat
            return allPhotos
        end tell '''

    args = ['2', '2']

    p = Popen(['osascript', '-'] + args, stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    stdout, stderr = p.communicate(scpt)
    output = stdout.split(',')
    trimedOutput = []
    for a in output:
        trimedOutput.append(a.strip())
    return trimedOutput

def execCommand(command):
    p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    stdout, stderr = p.communicate()
    return p.returncode, stdout, stderr

def getFiles(src_dir):
    files = ls(src_dir)
    # print(files)
    return files

def getPhotos():
    photos=listPhotos()
    # print(photos)
    return photos

def process(src_dir, tgt_dir, raw, command):
    photos = getPhotos()
    files = getFiles(src_dir)
    for f in files:
        fname, fextension = os.path.splitext(f)
        if len(raw)>0:
            raw_dir = raw
        else:
            raw_dir = src_dir

        if fextension.upper() in ['.JPEG','.PNG']:
            if (fname+fextension.lower() in photos) or (fname+fextension.upper() in photos):
                print(f)
                returncode, stdout, stderr = execCommand(command + [src_dir+'/'+f, tgt_dir])

                rawfile = Path(raw_dir + '/' + fname + ".RW2")
                # print("RAWFILE:" + str(rawfile))
                if (rawfile).is_file():
                    # print("RAW: "+f)
                    returncode, stdout, stderr = execCommand(command + [rawfile, tgt_dir])

@click.group()
def imgorg():
    pass

@imgorg.command()
@click.argument('src_dir', required=True)
@click.argument('tgt_dir', required=True)
@click.option('-r', '--raw', default='', help='Source folder of RAW files, if different from src_dir')
def simlink(src_dir, tgt_dir, raw):
    process(src_dir, tgt_dir, raw, ['ln', '-s'])

@imgorg.command()
@click.argument('src_dir', required=True)
@click.argument('tgt_dir', required=True)
@click.option('-r', '--raw', default='', help='Source folder of RAW files, if different from src_dir')
def mv(src_dir, tgt_dir, raw):
    process(src_dir, tgt_dir, raw, ['mv'])

@imgorg.command()
@click.argument('src_dir', required=True)
@click.argument('tgt_dir', required=True)
def cmp(src_dir, tgt_dir):
    srcFiles = getFiles(src_dir)
    tgtFiles = getFiles(tgt_dir)

    for f in srcFiles:
        if f in tgtFiles:
            print("!!! File exists in both folders: " + f)

if __name__ == '__main__':
    imgorg()
