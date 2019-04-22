from subprocess import Popen, PIPE
from pathlib import Path
import click
import os

# set photoList to {"/Users/vitazak/Pictures/2018_Nepal_India/test/a/small_P1020589e.jpg", "/Users/vitazak/Pictures/2018_Nepal_India/test/a/small_P1020598e.jpg"}

def getSelectedPhotos() -> list:
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

def buildImgList(dirList, imgNames) -> str:
    pathList = list()
    imgProcessed = 0
    imgFound = 0
    imgNotFound=0
    for img in imgNames:

        print("IMG TO FIND: " + img)
        found = False
        name, ext = os.path.splitext(img)
        imgProcessed = imgProcessed + 1
        #print("NAME: " + name)
        #print("EXT: " + ext)

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

        names = list()
        names.append('s_%se.jpg'%(name))
        names.append('small_%se.jpg'%(name))
        names.append('s_%s.jpg'%(name))
        names.append('small_%s.jpg'%(name))
        names.append('s_%se.jpeg'%(name))
        names.append('small_%se.jpeg'%(name))
        names.append('s_%s.jpeg'%(name))
        names.append('small_%s.jpeg'%(name))

        for dir in dirList:
            for n in names:
                f = Path(dir+"/"+n)
                if f.is_file():
                    pathList.append(str(f))
                    #print("FOUND: " + str(f) + "\n")
                    found = True
                    imgFound = imgFound + 1
                    break
            if found:
                break

        if not found:
            print("NOT FOUND: " + str(img) + "\n")
            imgNotFound = imgNotFound + 1

    print("TOTAL PROCESSED: %s, FOUND: %s, NOT FOUND: %s \n"%(str(imgProcessed), str(imgFound), str(imgNotFound)))
    return pathList

def listToApplescript(srcList) -> str:
    result = '{'
    for item in srcList:
        appleItem = '"%s"'%(str(item))
        result = result+appleItem+', '
    result = result[:-2]
    result = result + "}"
    return result

@click.group()
def composeAlbum():
    pass

@composeAlbum.command()
def list():
    photos = getSelectedPhotos()
    number = 0
    for photo in photos:
        number = number + 1
        click.echo("%s\t%s"%(str(number), photo))            

@composeAlbum.command()
@click.argument('album', required=True)
@click.argument('dirs', nargs=-1)
@click.option('-c', '--check', default='n', help='Dont add to album. Perform a check only.')
@click.option('-b', '--batch', default='y', help='Add all in on batch.')
def add(album, dirs, check, batch):
    dirList = list()
    for folder in dirs:
        #click.echo('Folder: %s' % (folder))
        dirList.append(folder)

    if batch.upper() == 'Y':
        photos = getSelectedPhotos()
        pathList = buildImgList(dirList, photos)

        #click.echo("paths:")
        #click.echo(listToApplescript(pathList))

        if check.upper() != 'Y':
            click.echo("DOING")
            x = addImagesToGallery(album, listToApplescript(pathList))
            click.echo(x)

    if batch.upper() == 'N':
        photos = getSelectedPhotos()

        for p in photos:
            photoList = list()
            photoList.append(p)
            pathList = buildImgList(dirList, photoList)

            if check.upper() != 'Y':
                #click.echo("DOING")
                x = addImagesToGallery(album, listToApplescript(pathList))
                click.echo(x)

if __name__ == '__main__':
    composeAlbum()
