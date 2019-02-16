#!/usr/bin/env python3

import pygame, sys, pickle
import time, os, shutil, imghdr

photosDir = '/home/pi/Documents/Photos'
localGoodDir = '/home/pi/Downloads/img/good'
localBadDir = '/home/pi/Downloads/img/bad'
buGoodDir = '/media/pi/storage/Stuff/classified/good'
buBadDir = '/media/pi/storage/Stuff/classified/bad'
stagingDir = '/home/pi/Documents/staging'
imgDir = '/home/pi/Downloads/img'
cneeingDir = '/home/pi/Documents/cneeing'
cneedDir = '/home/pi/Documents/cneed'
imageSigsFile = '/home/pi/Documents/logs/imageSigs'

def getFeatures(pic):
    picture = pygame.image.load(stagingDir + '/' + pic)
    w = picture.get_width()
    h = picture.get_height()
    picString = pygame.image.tostring(picture, 'RGB')
    l = len(picString)
    s = sum(picString)
    a = s/l
    # print(str(w)+', '+str(h)+', '+str(l)+', '+str(s)+', '+pic)
    features = (w, h, l, s, a, pic)
    return features

def loadList(listFile):
    # loads codeList from listFile
    print("loading list file " + listFile)
    with open(listFile, 'rb') as fp:
        codeList = pickle.load(fp)
    print("This list has " + str(len(codeList)) + " codes")
    return codeList

def writeList(codeList, listFile):
    # saves codeList to listFile
    with open(listFile, 'wb') as fp:
        pickle.dump(codeList, fp)

def moveFiles():
    # moves files from the local classified folders to storage
    # if a file already exists in storage, delete it instead
    # move good files to staging for final evaluation
    badList = os.listdir(buBadDir)
    fileList = os.listdir(localBadDir)
    for pic in fileList:
        # log.debug("checking for bad file in storage: " + pic)
        try:
            badList.index(pic)
        except:
            # log.debug("Moving bad file to storage: " + pic)
            shutil.copy(localBadDir + '/' + pic, buBadDir)
        finally:
            os.remove(localBadDir + '/' + pic)
    goodList = os.listdir(buGoodDir)
    fileList = os.listdir(localGoodDir)
    for pic in fileList:
        # log.debug("checking for bad file in storage: " + pic)
        try:
            goodList.index(pic)
        except:
            # log.debug("Moving bad file to storage: " + pic)
            shutil.copy(localGoodDir + '/' + pic, buGoodDir)
            shutil.copy(localGoodDir + '/' + pic, stagingDir)
        finally:
            os.remove(localGoodDir + '/' + pic)

def cleanDir(targetDir):
    # remove files from targetDir that are not jpg or png
    fileList = os.listdir(targetDir)
    renamed = removed = 0
    for img in fileList:
        if os.path.isfile(targetDir + '/' + img):
            splits = img.split('?') # if name contains a ? we rename it
            if len(splits) >1:
                os.rename(targetDir + '/' + img, targetDir + '/' + splits[0])
                img = splits[0]
                renamed += 1
            if not img.endswith(".jpg") and not img.endswith(".png") \
                and not img.endswith(".jpeg"):
                fileType = imghdr.what(targetDir + '/' + img)
                if fileType not in ('jpeg', 'jpg', 'png'):
                    print("bad one " + img + ' - ' + str(fileType))
                    os.remove(targetDir + '/' + img)
                    removed += 1
    print('Renamed-' + str(renamed) + ', Removed-' + str(removed))

def cleanCneed():
    # remove files from cneed and cneeing folders
    fileList = os.listdir(cneedDir)
    for pic in fileList:
        os.remove(cneedDir + '/' + pic)
    fileList = os.listdir(cneeingDir)
    for pic in fileList:
        os.remove(cneeingDir + '/' + pic)

def dedupe():
    # checks file features against list of files that have been published
    # files that match signatures are deleted
    # files that do not match are moved to photos directory 
    # and added to the list     
    try: 
        imageSignatures = loadList(imageSigsFile)
    except:
        imageSignatures = []
    finally:
        writeList(imageSignatures, imageSigsFile)
    fileList = os.listdir(stagingDir)
    for img in fileList:
        if os.path.isfile(stagingDir + '/' + img):
            picSig = getFeatures(img)
            matched = False
            for i in imageSignatures:
                if picSig[-1] == i[-1]:
                    print(img + ' is a duplicate')
                    break
                elif picSig[0:-1] == i[0:-1]:
                    print(img+' is the same as '+i[-1])
                    matched = True
                    break
            if not matched:
                # print('added '+picSig[3])
                imageSignatures.append(picSig)
                shutil.copy(stagingDir + '/' + img, photosDir)
            os.remove(stagingDir + '/' + img)
    print('images in the set ' + str(len(imageSignatures)))
    writeList(imageSignatures, imageSigsFile)

# dedupe()
moveFiles()
cleanCneed()
cleanDir(imgDir)
