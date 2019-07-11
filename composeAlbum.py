from subprocess import Popen, PIPE
from pathlib import Path
import click
import os

# set photoList to {"/Users/vitazak/Pictures/2018_Nepal_India/test/a/small_P1020589e.jpg", "/Users/vitazak/Pictures/2018_Nepal_India/test/a/small_P1020598e.jpg"}

def ls(directory):
    ls = Popen(["ls", "-p", directory], stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    grep = Popen(["grep", "-v", "/$"],stdin=ls.stdout,stdout=PIPE)
    endOfPipe = grep.stdout

    files = []
    for line in endOfPipe:
        files.append(line.strip().decode('utf-8'))

    return files

def getFiles(src_dir):
    files = ls(src_dir)
    return files

def getAlbumPhotos(ref_album):
    print("*** GET ALBUM PHOTOS ***")
    scpt = '''
        tell application "Photos"
            set allPhotos to {}
            set allIds to {}
            set stats to {}

            set photosSelection to (get media items of album "%s")

            repeat with aPhoto in photosSelection
                set the photoProps to the properties of aPhoto
                set photoName to filename of photoProps
                copy (id of photoProps) to the end of the allIds
                copy (filename of photoProps) to the end of the allPhotos
            end repeat
            copy (count of photosSelection) to the end of the stats

            return {stats, allPhotos, allIds}

        end tell ''' % (ref_album)

    args = ['2', '2']

    p = Popen(['osascript', '-'] + args, stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    stdout, stderr = p.communicate(scpt)
    output = stdout.split(',')
    length = int(output[0])

    names = list()
    ids = list()

    for a in range (length):
        names.append(output[a+1].strip())
        #print("NAME: "+output[a+1].strip())
        ids.append(output[a+1+length].strip())
        #print("ID: "+output[a+1+length].strip())

    return names, ids

def getSelectedPhotos() -> list:
    print("*** GET SELECTED PHOTOS ***")
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
            set allIds to {}
            set stats to {}

            repeat with aPhoto in photosSelection
                set the photoProps to the properties of aPhoto
                set photoName to filename of photoProps
                copy (id of photoProps) to the end of the allIds
                copy (filename of photoProps) to the end of the allPhotos
            end repeat
            copy (count of photosSelection) to the end of the stats
            return {stats, allPhotos, allIds}
        end tell '''

    args = ['2', '2']

    p = Popen(['osascript', '-'] + args, stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    stdout, stderr = p.communicate(scpt)
    output = stdout.split(',')

    length = int(output[0])

    names = list()
    ids = list()

    for a in range (length):
        names.append(output[a+1].strip())
        # print("NAME: "+output[a+1].strip())
        ids.append(output[a+1+length].strip())
        # print("ID: "+output[a+1+length].strip())

    return names, ids

def addImagesToGallery(album, photosList):
    print("ALBUM: " + album)
    print("PHOTOS: " + photosList)
    scpt = '''
        set photoList to %s

        set imageList to {}

        repeat with aPhoto in photoList
            set filePath to POSIX file aPhoto
            copy filePath to the end of imageList
        end repeat

        repeat with i from 1 to number of items in imageList
            set this_item to item i of imageList as alias
        end repeat

        tell application "Photos"
            import imageList into container named "%s" with skip check duplicates
        end tell ''' % (photosList, album)

    args = ['2', '2']

    p = Popen(['osascript', '-'] + args, stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    stdout, stderr = p.communicate(scpt)
    output = stdout.split(',')
    trimedOutput = []
    for a in output:
        trimedOutput.append(a.strip())
    return trimedOutput

def buildFileNames(name):
    if name.upper().startswith('SMALL_'):
        name = name[6:]
    if name.upper().startswith('S_'):
        name = name[2:]
    if name.upper().endswith('E_80_TMP'):
        name = name[:-8]
    if name.upper().endswith('E_80_RAW'):
        name = name[:-8]
    if name.upper().endswith('E_RAW_80'):
        name = name[:-8]
    if name.upper().endswith('E_80_V2'):
        name = name[:-7]
    if name.upper().endswith('E_HDR'):
        name = name[:-5]
    if name.upper().endswith('E_RAW'):
        name = name[:-5]
    if name.upper().endswith('E_80'):
        name = name[:-4]
    if name.upper().endswith('E'):
        name = name[:-1]

    #print("NAME COMPOSED: " + name)

    names = list()
    names.append('s_%se.jpg'%(name))
    names.append('small_%se.jpg'%(name))
    names.append('s_%s.jpg'%(name))
    names.append('small_%s.jpg'%(name))
    names.append('%s.jpg'%(name))
    names.append('s_%se.jpeg'%(name))
    names.append('small_%se.jpeg'%(name))
    names.append('s_%s.jpeg'%(name))
    names.append('small_%s.jpeg'%(name))
    names.append('%s.jpeg'%(name))

    return names

def buildImgList(dirList, imgNames, refnames, refids):
    pathList = list()
    imgProcessed = 0
    imgFound = 0
    imgNotFound=0
    for img in imgNames:

        print("IMG TO FIND IN FOLDERS: " + img)
        found = False
        name, ext = os.path.splitext(img)
        imgProcessed = imgProcessed + 1
        #print("NAME: " + name)
        #print("EXT: " + ext)

        names = buildFileNames(name)

        existingIds = list()
        existingNames = list()

        for n in names:
            try:
                idx = refnames.index(n)
                existingIds.append(refids[idx])
                existingNames.append(n)
                print("FOUND IN REF ALBUM: " + n + " ID: " + refids[idx])
            except(Exception):
                None
                #print("NAME " + n + " doesnt exist in ref album")

        for dir in dirList:
            location = None
            for n in names:

                if n in existingNames:
                    found = True
                    imgFound = imgFound + 1
                    location = n
                    break

                f = Path(dir+"/"+n)
                if f.is_file():
                    pathList.append(str(f))
                    #print("FOUND: " + str(f) + "\n")
                    found = True
                    imgFound = imgFound + 1
                    location = str(f)
                    break
            if found:
                print("FOUND: " + location)
                break

        if not found:
            print("NOT FOUND: " + str(img) + "\n")
            imgNotFound = imgNotFound + 1

    print("TOTAL PROCESSED: %s, FOUND: %s, NOT FOUND: %s \n"%(str(imgProcessed), str(imgFound), str(imgNotFound)))
    return existingIds, pathList

def listToApplescript(srcList) -> str:
    result = '{'
    for item in srcList:
        appleItem = '"%s"'%(str(item))
        result = result+appleItem+', '
    result = result[:-2]
    result = result + "}"
    return result

@click.command()
@click.argument('album', required=True, nargs=1)
@click.argument('dirs', nargs=-1)
@click.option('-c', '--check', default='n', help='Dont add to album. Perform a check only.')
@click.option('-b', '--batch', default='y', help='Add all in on batch.')
@click.option('-a', '--ref_album', default='', help='Reference album to check if photo exists.')
def add(album, dirs, check, batch, ref_album):
    dirList = list()
    #batch = 'N'
    #check = 'Y'
    for folder in dirs:
        #click.echo('Folder: %s' % (folder))
        dirList.append(folder)

    photos, ids = getSelectedPhotos()
    refphotos, refids = getAlbumPhotos(ref_album)

    if batch.upper() == 'Y':

        pathList, idsToLink = buildImgList(dirList, photos, refphotos, refids)

        click.echo("paths:")
        click.echo(listToApplescript(pathList))

        if check.upper() != 'Y':
            click.echo("DOING")
            x = addImagesToGallery(album, listToApplescript(pathList))
            click.echo(x)

    if batch.upper() == 'N':

        for p in photos:
            photoList = list()
            photoList.append(p)
            pathList, idsToLink = buildImgList(dirList, photoList, refphotos, refids)

            if check.upper() != 'Y':
                #click.echo("DOING")
                x = addImagesToGallery(album, listToApplescript(pathList))
                click.echo(x)

if __name__ == '__main__':
    add()
