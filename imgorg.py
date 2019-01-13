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
    # print(files[0],files[1],files[2],files[3])
    return files

def getPhotos():
    photos=listPhotos()
    # print(photos[0],photos[1],photos[2],photos[3])
    return photos

def processRaw(raw_dir, tgt_dir, fname, command):
    rawfile1 = Path(raw_dir + '/' + fname + ".RW2")
    rawfile2 = Path(raw_dir + '/' + fname + ".RAF")
    returncode, stdout, stderr = -1,-1,-1
    rawpath = None
    # print("RAWFILE:" + str(rawfile))
    if (rawfile1).is_file():
        rawpath = os.path.abspath(rawfile1)
    if (rawfile2).is_file():
        rawpath = os.path.abspath(rawfile2)

    if not (rawpath is None):
        returncode, stdout, stderr = execCommand(command + [rawpath, tgt_dir])

    return returncode, stdout, stderr

def process(src_dir, tgt_dir, raw, command, process_jpeg, process_raw):
    photos = getPhotos()
    files = getFiles(src_dir)

    if len(raw)>0 and process_jpeg.upper() == 'Y':
        raw_dir = raw
    else:
        raw_dir = src_dir

    for f in files:
        fname, fextension = os.path.splitext(f)

        if fextension.upper() in ['.JPEG','.JPG','.PNG'] and process_jpeg in ['y','Y']:
            if ((fname+fextension.lower() in photos) or (fname+fextension.upper() in photos)):
                src_path = os.path.abspath(src_dir)
                returncode, stdout, stderr = execCommand(command + [src_path+'/'+f, tgt_dir])

                if process_raw in ['y','Y']:
                    returncode, stdout, stderr = processRaw(raw_dir, tgt_dir, fname, command)

        if process_jpeg.upper() in ['N'] and process_raw.upper() in ['Y']:
            if (((fname+'.jpeg') in photos) or ((fname+'JPEG') in photos) or ((fname+'.jpg') in photos) or ((fname+'.JPG') in photos)):
                returncode, stdout, stderr = processRaw(raw_dir, tgt_dir, fname, command)

@click.group()
def imgorg():
    pass

@imgorg.command()
@click.argument('src_dir', required=True)
@click.argument('tgt_dir', required=True)
@click.option('-r', '--raw', default='', help='Source folder of RAW files, if different from src_dir')
@click.option('-t', '--type', default='', help='File type to process - JPEG, RAW, ALL')
def simlink(src_dir, tgt_dir, raw, type):
    process_jpeg = 'n'
    process_raw = 'n'
    if type is None or type.upper() in ['JPEG','ALL'] or type:
        process_jpeg = 'y'
    if type is None or type.upper() in ['RAW','ALL']:
        process_raw = 'y'
    process(src_dir, tgt_dir, raw, ['ln', '-s'], process_jpeg, process_raw)

@imgorg.command()
@click.argument('src_dir', required=True)
@click.argument('tgt_dir', required=True)
@click.option('-t', '--type', default='', help='File type to process - JPEG, RAW, ALL')
def cp(src_dir, tgt_dir, type):
    process_jpeg = 'n'
    process_raw = 'n'
    print('type: ' + type)
    if type is None or type.upper() in ['JPEG','ALL']:
        process_jpeg = 'y'
    if type is None or type.upper() in ['RAW','ALL']:
        process_raw = 'y'
    print('jpeg: ' + process_jpeg + ', raw: ' + process_raw)
    process(src_dir, tgt_dir, type, ['cp'], process_jpeg, process_raw)

@imgorg.command()
@click.argument('src_dir', required=True)
@click.argument('tgt_dir', required=True)
@click.option('-r', '--raw', default='', help='Source folder of RAW files, if different from src_dir')
def mv(src_dir, tgt_dir, raw):
    process(src_dir, tgt_dir, raw, ['mv'], 'y', 'y')

@imgorg.command()
@click.argument('src_dir', required=True)
@click.argument('tgt_dir', required=True)
def cmp(src_dir, tgt_dir):
    if src_dir == 'PHOTOS':
        srcFiles = getPhotos()
    else:
        srcFiles = getFiles(src_dir)

    if tgt_dir == 'PHOTOS':
        tgtFiles = getPhotos()
    else:
        tgtFiles = getFiles(tgt_dir)

    for f in srcFiles:
        if f in tgtFiles:
            #print("!!! File exists in both folders: " + f)
            pass
        else:
            pass
            print("!!! File found only in source : " + f)

    for f in tgtFiles:
        if f in srcFiles:
            #print("!!! File exists in both folders: " + f)
            pass
        else:
            pass
            print("!!! File found only in target : " + f)

@imgorg.command()
@click.argument('src_dir', required=True)
@click.argument('tgt_dir', required=True)
def resize(src_dir, tgt_dir):
    command = 'jpeg-recompress'
    files = getFiles(src_dir)
    for f in files:
        fname, fextension = os.path.splitext(f)
        if fextension.upper() in ['.JPEG','.JPG','.PNG']:
            returncode, stdout, stderr = execCommand([command, src_dir+'/'+f, tgt_dir+'/small_'+f])
            print(f, returncode, stdout)
if __name__ == '__main__':
    imgorg()
