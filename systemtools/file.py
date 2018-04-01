# coding: utf-8

import os, errno
import shutil
import re
import time
from enum import Enum
import pickle
import string

from systemtools.location import isFile, getDir, isDir, sortedGlob, decomposePath, tmpDir
from systemtools.basics import getRandomStr


class TIMESPENT_UNIT(Enum):
    DAYS = 1
    HOURS = 2
    MINUTES = 3
    SECONDS = 4
def getLastModifiedTimeSpent(path, timeSpentUnit=TIMESPENT_UNIT.HOURS):
    diff = time.time() - os.path.getmtime(path)
    if timeSpentUnit == TIMESPENT_UNIT.SECONDS:
        return diff
    diff = diff / 60.0
    if timeSpentUnit == TIMESPENT_UNIT.MINUTES:
        return diff
    diff = diff / 60.0
    if timeSpentUnit == TIMESPENT_UNIT.HOURS:
        return diff
    diff = diff / 24.0
    if timeSpentUnit == TIMESPENT_UNIT.DAYS:
        return diff

def purgeOldFiles(pattern, maxTimeSpent, timeSpentUnit=TIMESPENT_UNIT.SECONDS):
    allPlugins = sortedGlob(pattern)
    for current in allPlugins:
        timeSpent = getLastModifiedTimeSpent(current, timeSpentUnit)
        if timeSpent > maxTimeSpent:
            removeFile(current)

def strToFileName(*args, **kwargs):
    return strToFilename(*args, **kwargs)

def strToFilename(text):
    """

    https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
    """
    text = text.replace(" ", "_")
    valid_chars = "-_.()%s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in text if c in valid_chars)

def serialize(obj, path):
    with open(path, 'wb') as handle:
        pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)

def deserialize(path):
    with open(path, 'rb') as handle:
        return pickle.load(handle)

def getAllNumbers(text):
    """
        This function is a copy of systemtools.basics.getAllNumbers
    """
    if text is None:
        return None
    allNumbers = []
    if len(text) > 0:
        # Remove space between digits :
        spaceNumberExists = True
        while spaceNumberExists:
            text = re.sub('(([^.,0-9]|^)[0-9]+) ([0-9])', '\\1\\3', text, flags=re.UNICODE)
            if re.search('([^.,0-9]|^)[0-9]+ [0-9]', text) is None:
                spaceNumberExists = False
        numberRegex = '[-+]?[0-9]+[.,][0-9]+|[0-9]+'
        allMatchIter = re.finditer(numberRegex, text)
        if allMatchIter is not None:
            for current in allMatchIter:
                currentFloat = current.group()
                currentFloat = re.sub("\s", "", currentFloat)
                currentFloat = re.sub(",", ".", currentFloat)
                currentFloat = float(currentFloat)
                if currentFloat.is_integer():
                    allNumbers.append(int(currentFloat))
                else:
                    allNumbers.append(currentFloat)
    return allNumbers


def mkdir(path):
    mkdirIfNotExists(path)

def mkdirIfNotExists(path):
    """
        This function make dirs recursively like mkdir -p in bash
    """
    os.makedirs(path, exist_ok=True)

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

def replaceInFile(path, listSrc, listRep):
    with open(path, 'r') as f :
        filedata = f.read()
    for i in range(len(listSrc)):
        src = listSrc[i]
        rep = listRep[i]
        filedata = filedata.replace(src, rep)
    with open(path, 'w') as f:
        f.write(filedata)

def fileExists(filePath):
    return os.path.exists(filePath)

def globRemove(globPattern):
    filesPaths = sortedGlob(globPattern)
    removeFiles(filesPaths)

def removeFile(path):
    if not isinstance(path, list):
        path = [path]
    for currentPath in path:
        try:
            os.remove(currentPath)
        except OSError:
            pass
def removeFiles(path):
    removeFile(path)
def removeAll(path):
    removeFile(path)

def fileToStr(path, split=False):
    if split:
        return fileToStrList(path)
    else:
        with open(path, 'r') as myfile:
            data = myfile.read()
        return data

def fileToStrList_old(path, strip=True):
    data = fileToStr(path)
    if strip:
        data = data.strip()
    return data.splitlines()

def fileToStrList(*args, removeDuplicates=False, **kwargs):
    result = fileToStrListYielder(*args, **kwargs)
    if removeDuplicates:
        return list(set(list(result)))
    else:
        return list(result)

def basicLog(text, logger, verbose):
    if verbose:
        if text is not None and text != "":
            if logger is None:
                print(text)
            else:
                logger.info(text)

def fileToStrListYielder(path,
                         strip=True,
                         skipBlank=True,
                         commentStart="###",
                         logger=None,
                         verbose=True):

    if path is not None and isFile(path):
        commentCount = 0
        with open(path) as f:
            for line in f.readlines():
                isComment = False
                if strip:
                    line = line.strip()
                if commentStart is not None and len(commentStart) > 0 and line.startswith(commentStart):
                    commentCount += 1
                    isComment = True
                if not isComment:
                    if skipBlank and len(line) == 0:
                        pass
                    else:
                        yield line
        if verbose and commentCount > 0:
            basicLog("We found " + str(commentCount) + " comments in " + path, logger, verbose)
    else:
        if verbose:
            basicLog(str(path) + " file not found.", logger, verbose)


def removeIfExists(path):
    try:
        os.remove(path)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred
def removeIfExistsSecure(path, slashCount=5):
    if path.count('/') >= slashCount:
        removeIfExists(path)

def removeTreeIfExists(path):
    shutil.rmtree(path, True)
def removeTreeIfExistsSecure(path, slashCount=5):
    if path.count('/') >= slashCount:
        removeTreeIfExists(path)

def strListToTmpFile(theList, *args, **kwargs):
    text = ""
    for current in theList:
        text += current + "\n"
    return strToTmpFile(text, *args, **kwargs)

def strToTmpFile(text, name=None, ext="", addRandomStr=False, *args, **kwargs):
    if text is None:
        text = ""
    if ext is None:
        ext = ""
    if ext != "":
        if not ext.startswith("."):
            ext = "." + ext
    if name is None:
        name = getRandomStr()
    elif addRandomStr:
        name += "-" + getRandomStr()
    path = tmpDir(*args, **kwargs) + "/" + name + ext
    strToFile(text, path)
    return path

def strToFile(text, path):
#     if not isDir(getDir(path)) and isDir(getDir(text)):
#         path, text = text, path
    if isinstance(text, list):
        text = "\n".join(text)
    textFile = open(path, "w")
    textFile.write(text)
    textFile.close()

def normalizeNumericalFilePaths(globRegex):
    """
        This function get a glob path and rename all file1.json file2.json ... file20.json
        to file01.json file02.json ... file20.json to better sort the folder by file names
    """
    # We get all paths:
    allPaths = sortedGlob(globRegex)
    allNumbers = []
    # We get all ints:
    for path in allPaths:
        # Get the filename without extension:
        (dir, filename, ext, filenameExt) = decomposePath(path)
        # Get all numbers:
        currentNumbers = getAllNumbers(filename)
        # Check if we have a int first:
        if currentNumbers is None or len(currentNumbers) == 0:
            print("A filename has no number.")
            return False
        firstNumber = currentNumbers[0]
        if not isinstance(firstNumber, int):
            print("A filename has no float as first number.")
            return False
        # Add it in the list:
        allNumbers.append(firstNumber)
    # Get the max int:
    maxInt = max(allNumbers)
    # Calculate the nmber of digit:
    digitCountHasToBe = len(str(maxInt))
    # Replace all :
    i = 0
    for i in range(len(allNumbers)):
        currentPath = allPaths[i]
        (dir, filename, ext, filenameExt) = decomposePath(currentPath)
        currentInt = allNumbers[i]
        currentRegex = "0*" + str(currentInt)
        zerosCountToAdd = digitCountHasToBe - len(str(currentInt))
        zerosStr = "0" * zerosCountToAdd
        newFilename = re.sub(currentRegex, zerosStr + str(currentInt), filename, count=1)
        newFilename = dir + newFilename + "." + ext
        if currentPath != newFilename:
            os.rename(currentPath, newFilename)
            print(newFilename + " done.")
        i += 1
    return True


if __name__ == '__main__':
#     normalizeNumericalFilePaths("/home/hayj/test/test1/*.txt")
#     normalizeNumericalFilePaths("/users/modhel/hayj/NoSave/Data/TwitterArchiveOrg/Converted/*.bz2")
    strToTmpFile("hoho", subDir="test", ext="txt")
    strToFile("haha", tmpDir(subDir="test") + "/test.txt")





