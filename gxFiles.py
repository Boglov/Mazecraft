import os
import csv
from pathlib import Path

homeDir = os.path.dirname(os.path.realpath(__file__))
cfgFile = homeDir + "/config.cfg"

def LoadFile(fPath):
    fixedPath = Path(fPath)

    with open(fixedPath, mode="r") as f:
        loadedData = enumerate(csv.reader(f))
        datas = []
        for x, data in loadedData:
            print(datas.append(data))

    return datas

def WriteFile(fPath, dataList):
    fixedPath = Path(fPath)

    with open(fixedPath, mode="w+") as f:
        dIndex = 0

        for data in dataList:

            csvLine = "%s"%(str(data).replace('[', ''))
            csvLine = "%s"%(str(csvLine).replace(']', ''))
            csvLine += "\n"
            print(csvLine)
            f.write(csvLine)
            dIndex += 1
    print("Wrote to:%s"%fPath)

# Write a single csv line to a given file
def AppendFile(fPath, cTag, cID, cVal):
    newLine = "%s,%s,%s"%(str(cTag), str(cID), str(cVal))
    print(newLine)

    fixedPath = Path(fPath)
    with open(fixedPath, mode="a") as f:
        f.write(newLine+"\n")

        #for line in mData:
            #f.write(line)
            #f.write("\n")

def Split2DList(theList):
    csvList = []
    for list in theList:
        for item in list:
            csvList.append(str(item).split(","))

    return csvList

def Print2DList(theList):
    csvList = []
    for list in theList:
        for item in list:
            csvList.append(str(item).split(","))

    return csvList

