import pygame
from pygame.locals import *
import os
import tkinter
import csv

from math import radians, degrees
from pathlib import Path
from tkinter import filedialog as FD
from gxColors import *
from gxElements import *

homeDir = os.path.dirname(os.path.realpath(__file__))

mapDir = homeDir + "/CustomMaps/"
levelDir = homeDir + "/data/Levels/"
menuMapDir = homeDir + "/data/MenuMaps/"

GRIDCOLOR = BLACK

defaultDoorColors = []
for dColors in range(5):
    defaultDoorColors.append(GetRandomColor())

defaultPortalColors = []
for pColors in range(5):
    defaultPortalColors.append(GetRandomColor())

# Define block types
EMPTYBLOCK = "Empty"
STARTBLOCK = "Start"
FINISHBLOCK = "Finish"
WALLBLOCK = "Wall"
DOORBLOCK = "Door"
KEYBLOCK = "Key"
PORTALBEGIN = "Portal Begin"
PORTALEND = "Portal End"

dCellsize = 30

def clip(val, min, max):
    if val < min:
        val = min
    elif val > max:
        val = max
    return val

class Cell:
    def __init__(self, bType, gX=-1, gY=-1, bID=0):
        self.gridX = gX
        self.gridY = gY
        self.blockType = bType
        self.id = bID
        self.saveChar = "##"

        if self.blockType == STARTBLOCK:
            self.saveChar = "S" + str(self.id)

        elif self.blockType == FINISHBLOCK:
            self.saveChar = "FF"

        elif self.blockType == WALLBLOCK:
            self.saveChar = "WW"

        elif self.blockType == DOORBLOCK:
            self.saveChar = "D" + str(self.id)

        elif self.blockType == KEYBLOCK:
            self.saveChar = "K" + str(self.id)

        elif self.blockType == PORTALBEGIN:
            self.saveChar = "p" + str(self.id)

        elif self.blockType == PORTALEND:
            self.saveChar = "P" + str(self.id)

    def GetSaveChar(self):
        if self.blockType == STARTBLOCK:
            self.saveChar = "S" + str(self.id)

        elif self.blockType == FINISHBLOCK:
            self.saveChar = "FF"

        elif self.blockType == WALLBLOCK:
            self.saveChar = "WW"

        elif self.blockType == DOORBLOCK:
            self.saveChar = "D" + str(self.id)

        elif self.blockType == KEYBLOCK:
            self.saveChar = "K" + str(self.id)

        elif self.blockType == PORTALBEGIN:
            self.saveChar = "p" + str(self.id)

        elif self.blockType == PORTALEND:
            self.saveChar = "P" + str(self.id)

        return self.saveChar

    def Clear(self):
        self.blockType = EMPTYBLOCK
        self.id = 0
        self.saveChar = "##"

class Map:
    defCellsize = dCellsize

    def __init__(self, dSurf, r=19, c=13, cSize = 30, x=0, y=0, gToggle=True):
        self.mapSurface = dSurf
        self.handle = (x, y)
        self.rows = r
        self.cols = c
        self.cellSize = cSize

        # Initialize an empty grid of cells according
        # to row and column inputs
        self.cellsNew = [[Cell(EMPTYBLOCK, thisLine, thisCol) for thisLine in range(r)] for thisCol in range(c)]

        self.doorColors = defaultDoorColors
        self.portalColors = defaultPortalColors
        self.wallColor = GetRandomColor()
        self.playerColor = GetRandomColor()
        self.playerEyeColor = BLUE
        self.finishColor = GetRandomColor()
        self.startCell = Cell(STARTBLOCK, -1, -1)
        self.finishCell = Cell(FINISHBLOCK, -2, -2)
        self.startDirection = 0

        self.eTotalDoors = 0
        self.eTotalKeys = 0
        self.eTotalPortalBegins = 0
        self.eTotalPortalEnds = 0

        self.eCurrentDoorIndex = 0
        self.eCurrentKeyIndex = 0
        self.eCurrentPortalBeginIndex = 0
        self.eCurrentPortalEndIndex = 0

        # These store the cell ids upon deletion
        # to allow the player to re-place the
        # corresponding object easily

        self.doorRemovalQue = []
        self.keyRemovalQue = []
        self.portalBeginRemovalQue = []
        self.portalEndRemovalQue = []

        self.editMode = gToggle
        self.mouseMapPos = (0,0)
        self.editSelect = 0
        self.uiBuffer = 100
        self.filePath = mapDir + 'untitled.gmf'
        self.mapWidth = self.cellSize*self.rows
        self.mapHeight = self.cellSize*self.cols
        self.totalHeight = self.mapHeight + self.uiBuffer

        self.finishMarkerText = GX_Text(dSurf, "Finish", BLACK, (0,0), int(cSize/3)-1)
        self.dragPlacing = False
        self.dragDeleting = False

        self.scores = []
        self.currentBest = 0

    def RemoveAllScores(self, pathList):
        fileCounter = 0
        removedScoreCount = 0
        unremovedScores = 0

        for path in pathList:

            lineCounter = 0

            fileCounter += 1
            lines = []
            linesAfterRemoval = []

            with open(path, mode="r+") as f:
                lines = f.readlines()

                for line in lines:
                    thisChar = line[0]
                    if(thisChar == 'h'):
                        removedScoreCount += 1
                    if(thisChar != 'h' and thisChar != ' '):
                        linesAfterRemoval.append(line)

            #tempF = levelDir + "/Cleaned/cleaned%d.gmf"%fileCounter

            if removedScoreCount != 0:
                with open(path, mode="w+") as ft:
                    for fLine in linesAfterRemoval:
                        ft.write(fLine)

        if(removedScoreCount != 0):
            #print("Removed %d"%removedScoreCount, "scores from %d"%fileCounter, "levels.")
            noteStr = "Removed %d "%removedScoreCount + "scores from %d"%fileCounter + " levels."
            print(noteStr)
            return True
        else:
            print("No scores to remove")
            return False

    def AddScore(self, lTime):
        cBest = self.GetBestScore()
        previousBest = 0
        previousScore = 0
        thisScore = round(lTime, 3)
        print("Score: " + str(thisScore))
        scoreDiff = 0

        previousBest = self.GetBestScore()
        previousScore = self.GetLastScore()

        scoreDiff = round(previousBest-thisScore,2)
        print("Score difference from best run: %d" % scoreDiff)
        self.scores.append(thisScore)

        # If the new score is better than the previous best
        # or there are no other scores, save the new score
        if scoreDiff > 0 or cBest == 0:
            with open(self.filePath, mode="a") as f:
                fixedLine = "h," + str(thisScore)
                #print(fixedLine)
                f.write("\n"+str(fixedLine))

            print("Previous score: ", previousScore)
            print("Previous Best:", previousBest)
            print("You beat your previous Highscore by ", str(scoreDiff), "seconds!")

    def GetLastScore(self):
        lastScore = 0
        if len(self.scores) > 0:
            lastScore = self.scores[-1]

        return lastScore

    def GetBestScore(self):
        bestScore = 0
        if len(self.scores) > 0:
            bestScore = min(self.scores)

        return bestScore

    # Takes grid coordinates and
    # returns exact position
    def GetRealPoint(self, gX, gY):
            realX = gX*self.cellSize
            realY = gY*self.cellSize
            realPos = (realX, realY)
            return realPos

    # Takes exact position and
    # returns grid coordinates
    def GetMapPoint(self, rX, rY):
        gPoint = (-1, -1)
        gX=-1
        gY=-1
        if rX < self.mapWidth :
            gX = clip(int(rX/self.cellSize), 0, self.rows-1)
            #print(gPoint)

        if rY < self.mapHeight:
            gY = clip(int(rY/self.cellSize), 0, self.cols-1)
            #print(gPoint)

        thisCell = self.cellsNew[gY][gX]
        gPoint = (gX,gY)
        return gPoint

    def GetPortalEnd(self, pID):
        print("Teleporting")
        otherExists = False
        for row in self.cellsNew:
            for cell in row:
                if cell.blockType == PORTALEND:
                    if cell.id == pID:
                        pEnd = (cell.gridX,cell.gridY)
                        print(pEnd)
                        otherExists = True
                        return pEnd
        if not otherExists:
            return None

    def GetPortalBegin(self, pID):
        print("Teleporting back")
        otherExists = False
        for row in self.cellsNew:
            for thisCell in row:
                if thisCell.blockType == PORTALBEGIN:
                    if thisCell.id == pID:
                        pBegin = (thisCell.gridX,thisCell.gridY)
                        otherExists = True
                        return pBegin
        if not otherExists:
            return None

    def GetBlockID(self, gX, gY):
        bID = self.cellsNew[gY][gX].id
        return bID

    def CheckFor(self, bType, gX, gY, log=False):
        if self.cellsNew[gY][gX].blockType == bType:
            if log == True:
                print(self.cellsNew[gY][gX].blockType)
            return True
        else:
            return False

    def CreateSaveData(self):
        sData = []
        thisLine = ''
        rCounter = 0
        # Loop through cells and generate save data
        # with a new line for each row
        for c in range(self.cols):
            thisLine = ''
            for r in range(self.rows):
                thisCell = self.cellsNew[c][r]

                if thisCell.blockType == STARTBLOCK:
                    thisCell.id = self.startDirection
                thisLine += thisCell.GetSaveChar()
                if r != self.rows-1:
                    thisLine += ','
            print(thisLine)

            sData.append(thisLine)

        # The rest of the data defines the
        # colors to be used when drawing the map

        # Wall color first
        wallColor = str(self.wallColor[0]) + "," + str(self.wallColor[1]) + "," + str(self.wallColor[2])
        sData.append("c,Wall,"+wallColor)

        # Player color second
        plColor = str(self.playerColor[0]) + "," + str(self.playerColor[1]) + "," + str(self.playerColor[2])
        sData.append("c,Player,"+plColor)

        # Finish cell color third
        finColor = str(self.finishColor[0]) + "," + str(self.finishColor[1]) + "," + str(self.finishColor[2])
        sData.append("c,Finish,"+finColor)

        # Door colors fourth
        dcIndex = 0
        for dColor in self.doorColors:
            cLine = str(dColor[0]) + "," + str(dColor[1]) + "," + str(dColor[2])
            sData.append("c,Door," + str(dcIndex) + "," + cLine)
            dcIndex +=1

        # Portal colors fifth
        pcIndex = 0
        for pColor in self.portalColors:
            cLine = str(pColor[0]) + "," + str(pColor[1]) + "," + str(pColor[2])
            sData.append("c,Portal," + str(pcIndex) + "," + cLine)
            pcIndex +=1

        # Lastly scores
        for score in self.scores:
            roundedScore = round(score, 3)
            fixedLine = "h," + str(roundedScore)
            sData.append(fixedLine)
        # print(sData)
        return sData

    def SaveMap(self, fPath):
        fixedPath = Path(fPath)

        if self.editMode == True:
            print("Saving ", fixedPath)
            mData = self.CreateSaveData()

            self.filePath = fixedPath

            with open(fixedPath, mode="w") as f:
                for line in mData:
                    f.write(line)
                    f.write("\n")
            print("Map saved to ", self.filePath)

        if not self.finishCell == None:
            print("F x:%d y:%d" % (self.finishCell.gridX, self.finishCell.gridY))

        print("S x:%d y:%d" % (self.startCell.gridX, self.startCell.gridY))

    def AskSaveMap(self):
        success = False
        if self.editMode == True:
            root = tkinter.Tk()
            files = [('Map Files', '*.gmf')]
            savePath = FD.asksaveasfile( initialdir = mapDir, filetypes = files, defaultextension = files)
            root.destroy()
            if not savePath == None:
                print(savePath)
                self.filePath = savePath
                self.SaveMap(savePath.name.strip())
                pygame.display.set_caption(os.path.split(savePath.name)[1])
                success = True
        return success

    def ClearBlock(self, gX, gY):

        c =  self.cellsNew[gY][gX]

        if self.editMode == True:
            if c.blockType == DOORBLOCK:
                self.eTotalDoors -= 1

                self.doorRemovalQue.append(c.id)
                self.eCurrentDoorIndex = self.doorRemovalQue[len(self.doorRemovalQue)-1]
                print("DQ:", self.doorRemovalQue)

            elif c.blockType == KEYBLOCK:
                self.eTotalKeys -= 1

                self.keyRemovalQue.append(c.id)
                self.eCurrentKeyIndex = self.keyRemovalQue[len(self.keyRemovalQue)-1]
                print("KQ:", self.keyRemovalQue)

            elif c.blockType == PORTALBEGIN:
                self.eTotalPortalBegins -= 1

                self.portalBeginRemovalQue.append(c.id)
                self.eCurrentPortalBeginIndex = self.portalBeginRemovalQue[len(self.portalBeginRemovalQue)-1]
                print("PBQ:", self.portalBeginRemovalQue)

            elif c.blockType == PORTALEND:
                self.eTotalPortalEnds -= 1

                self.portalEndRemovalQue.append(c.id)
                self.eCurrentPortalEndIndex = self.portalEndRemovalQue[len(self.portalEndRemovalQue)-1]
                print("PEQ:", self.portalEndRemovalQue)

        c.Clear()
        self.ListIndices()

    def ClearMap(self):
        for r in self.cellsNew:
            for thisCell in r:
                thisCell.Clear()

        self.eTotalDoors = 0
        self.eTotalKeys = 0
        self.eTotalPortalBegins = 0
        self.eTotalPortalEnds = 0
        self.eCurrentDoorIndex = 0
        self.eCurrentKeyIndex = 0
        self.eCurrentPortalBeginIndex = 0
        self.eCurrentPortalEndIndex = 0
        self.doorRemovalQue = []
        self.keyRemovalQue = []
        self.portalBeginRemovalQue = []
        self.portalEndRemovalQue = []


    def AssignCell(self, gPos, bType, bID = 0):
        c = self.cellsNew[gPos[1]][gPos[0]]

        # If the start point is clicked after placement
        # rotate the player
        if bType == STARTBLOCK:
            if c.blockType == STARTBLOCK:
                self.startDirection += 1
                if self.startDirection > 3:
                    self.startDirection = 0
                self.startCell.id = self.startDirection
            else:
                oldStartPos = self.startCell
                self.ClearBlock(oldStartPos.gridX, oldStartPos.gridY)
                c.blockType = bType
                c.id = self.startDirection
                self.startCell = c

        # If the finish block is placed at a new location
        # clear the old one as there can only be one
        # finish cell
        elif bType == FINISHBLOCK:
            if not self.finishCell == None:
                oldFinPos = self.finishCell
                self.ClearBlock(oldFinPos.gridX, oldFinPos.gridY)
            c.blockType = bType
            c.id = bID
            self.finishCell = c

        # Check if assigning a new start or finish cell
        # and if so remove the old one
        elif bType == WALLBLOCK:
            c.blockType = bType
            c.id = bID

        elif bType == DOORBLOCK:
            if not c.blockType == DOORBLOCK:
                self.ClearBlock(gPos[0],gPos[1])

                self.eTotalDoors += 1

                if len(self.doorRemovalQue) > 0:
                    self.doorRemovalQue.pop(-1)

                if len(self.doorRemovalQue) > 0:
                    self.eCurrentDoorIndex = self.doorRemovalQue[len(self.doorRemovalQue)-1]
                else:
                    self.eCurrentDoorIndex = self.eTotalDoors

                #print("DQ:", self.doorRemovalQue)

                if self.eTotalDoors >= len(self.doorColors):
                    self.doorColors.append(GetRandomColor())

                c.blockType = bType
                c.id = bID
            #else:
                #print("Door ID:", c.id)

        elif bType == KEYBLOCK:
            if not c.blockType == KEYBLOCK:
                self.ClearBlock(gPos[0],gPos[1])

                self.eTotalKeys += 1

                if len(self.keyRemovalQue) > 0:
                    self.keyRemovalQue.pop(-1)

                if len(self.keyRemovalQue) > 0:
                    self.eCurrentKeyIndex = self.keyRemovalQue[len(self.keyRemovalQue)-1]
                else:
                    self.eCurrentKeyIndex = self.eTotalKeys

                #print("KQ:", self.keyRemovalQue)

                if self.eTotalKeys >= len(self.doorColors):
                    self.doorColors.append(GetRandomColor())


                c.blockType = bType
                c.id = bID
            #else:
                #print("Key ID:", c.id)

        elif bType == PORTALBEGIN:
            if not c.blockType == PORTALBEGIN:
                self.ClearBlock(gPos[0],gPos[1])

                self.eTotalPortalBegins += 1

                if len(self.portalBeginRemovalQue) > 0:
                    self.portalBeginRemovalQue.pop(-1)

                if len(self.portalBeginRemovalQue) > 0:
                    self.eCurrentPortalBeginIndex = self.portalBeginRemovalQue[len(self.portalBeginRemovalQue)-1]
                else:
                    self.eCurrentPortalBeginIndex = self.eTotalPortalBegins

                #print("PBQ:", self.portalBeginRemovalQue)

                if self.eTotalPortalBegins >= len(self.portalColors):
                    self.portalColors.append(GetRandomColor())

                c.blockType = bType
                c.id = bID

        elif bType == PORTALEND:
            if not c.blockType == PORTALEND:
                self.ClearBlock(gPos[0],gPos[1])

                self.eTotalPortalEnds += 1

                if len(self.portalEndRemovalQue) > 0:
                    self.portalEndRemovalQue.pop(-1)

                if len(self.portalEndRemovalQue) > 0:
                    self.eCurrentPortalEndIndex = self.portalEndRemovalQue[len(self.portalEndRemovalQue)-1]
                else:
                    self.eCurrentPortalEndIndex = self.eTotalPortalEnds

                #print("PEQ:", self.portalEndRemovalQue)

                if self.eTotalPortalEnds >= len(self.portalColors):
                    self.portalColors.append(GetRandomColor())

                c.blockType = bType
                c.id = bID
        if not self.finishCell == None:
            print("F x:%d y:%d" % (self.finishCell.gridX, self.finishCell.gridY))
        print("S x:%d y:%d" % (self.startCell.gridX, self.startCell.gridY))

        # print(c.gridX, c.gridY)
        # Print out all editor indices for debugging
        #print("Assigned:", bType, "to cell[" + str(c.gridX) + "][" + str(c.gridY) +"]")
        #print("Block ID:", c.id)
        # self.ListIndices()

    def Reset(self):
        resetMap = LoadMap(self.filePath, self.mapSurface)
        #resetMap.ListIndices()
        print("S x:%d y:%d" % (self.startCell.gridX, self.startCell.gridY))
        print("F x:%d y:%d" % (self.finishCell.gridX, self.finishCell.gridY))
        return resetMap

    def HandleEditorInput(self, event):
        if self.editMode == True:
            mousePos = pygame.mouse.get_pos()
            gMousePos = self.GetMapPoint(mousePos[0], mousePos[1])

            if event.type == KEYDOWN:
                if event.key == K_x and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.ClearMap()

            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragPlacing = False
                if event.button == 3:
                    self.dragDeleting = False

            if mousePos[1] < self.mapHeight:
                self.mouseMapPos = gMousePos

                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 3:
                        self.dragDeleting = True

                    elif event.button == 1:
                        self.dragPlacing = True

        # Handle drag placement of walls
        if(self.dragPlacing):
            if self.editSelect == 0: # Start Point
                self.AssignCell(gMousePos, STARTBLOCK)

            elif self.editSelect == 1: # Finish Point
                self.AssignCell(gMousePos, FINISHBLOCK)

            if self.editSelect == 2: # Walls
                self.AssignCell(gMousePos, WALLBLOCK)

            if self.editSelect == 3: # Doors
                self.AssignCell(gMousePos, DOORBLOCK, self.eCurrentDoorIndex)

            elif self.editSelect == 4: # Keys
                self.AssignCell(gMousePos, KEYBLOCK, self.eCurrentKeyIndex)

            if self.editSelect == 5: # Portal Begins
                self.AssignCell(gMousePos, PORTALBEGIN, self.eCurrentPortalBeginIndex)

            elif self.editSelect == 6: # Portal Ends
                self.AssignCell(gMousePos, PORTALEND, self.eCurrentPortalEndIndex)

        # Handle drag deletion of anything
        elif(self.dragDeleting):
            self.ClearBlock(gMousePos[0], gMousePos[1])

    def DrawEditSelectThumb(self, pos):
        if self.editSelect == 0: # Start Point
            self.DrawPlayerBlock(pos, self.startDirection)

        elif self.editSelect == 1: # Finish Point
            self.DrawFinishBlock(pos)

        elif self.editSelect == 2: # Walls
            self.DrawWallBlock(pos)

        elif self.editSelect == 3: # Doors
            blockID = self.eCurrentDoorIndex
            self.DrawDoorBlock(pos, blockID)

        elif self.editSelect == 4: # Keys
            blockID = self.eCurrentKeyIndex
            self.DrawKey(pos, blockID)

        elif self.editSelect == 5: # Portal Begins
            blockID = self.eCurrentPortalBeginIndex
            self.DrawPortalBlock(pos, blockID)

        elif self.editSelect == 6: # Portal Ends
            blockID = self.eCurrentPortalEndIndex
            self.DrawPortalBlock(pos, blockID, portalEnd = True)

        pygame.draw.rect(self.mapSurface, BLACK, (pos[0], pos[1], self.cellSize-1, self.cellSize-1),1)

    def DrawPlayerBlock(self, pos, facing):
        # Draw player replica to indicate
        # starting direction and player color
        pygame.draw.rect(self.mapSurface, self.playerColor, (pos[0], pos[1], self.cellSize-1, self.cellSize-1))
        pygame.draw.rect(self.mapSurface, BLACK, (pos[0], pos[1], self.cellSize-1, self.cellSize-1), 1)

        eyeSize = int(self.cellSize/5)

        if facing == 3:
            pygame.draw.rect(self.mapSurface, self.playerEyeColor, (pos[0]+5, pos[1]+5, eyeSize, eyeSize))
            pygame.draw.rect(self.mapSurface, self.playerEyeColor, (pos[0]+self.cellSize-eyeSize-8, pos[1]+5, eyeSize, eyeSize))

            pygame.draw.rect(self.mapSurface, BLACK, (pos[0]+5, pos[1]+5, eyeSize, eyeSize), 2)
            pygame.draw.rect(self.mapSurface, BLACK, (pos[0]+self.cellSize-eyeSize-8, pos[1]+5, eyeSize, eyeSize), 2)

        elif facing == 1:
            pygame.draw.rect(self.mapSurface, self.playerEyeColor, (pos[0]+5, pos[1]+self.cellSize-eyeSize-8, eyeSize, eyeSize))
            pygame.draw.rect(self.mapSurface, self.playerEyeColor, (pos[0]+self.cellSize-eyeSize-8, pos[1]+self.cellSize-eyeSize-8, eyeSize, eyeSize))

            pygame.draw.rect(self.mapSurface, BLACK, (pos[0]+5, pos[1]+self.cellSize-eyeSize-8, eyeSize, eyeSize), 2)
            pygame.draw.rect(self.mapSurface, BLACK, (pos[0]+self.cellSize-eyeSize-8, pos[1]+self.cellSize-eyeSize-8, eyeSize, eyeSize), 2)

        elif facing == 2:
            pygame.draw.rect(self.mapSurface, self.playerEyeColor, (pos[0]+5, pos[1]+5, eyeSize, eyeSize))
            pygame.draw.rect(self.mapSurface, self.playerEyeColor, (pos[0]+5, pos[1]+self.cellSize-eyeSize-8, eyeSize, eyeSize))

            pygame.draw.rect(self.mapSurface, BLACK, (pos[0]+5, pos[1]+5, eyeSize, eyeSize), 2)
            pygame.draw.rect(self.mapSurface, BLACK, (pos[0]+5, pos[1]+self.cellSize-eyeSize-8, eyeSize, eyeSize), 2)

        elif facing == 0:
            pygame.draw.rect(self.mapSurface, self.playerEyeColor, (pos[0]+self.cellSize-eyeSize-8, pos[1]+5, eyeSize, eyeSize))
            pygame.draw.rect(self.mapSurface, self.playerEyeColor, (pos[0]+self.cellSize-eyeSize-8, pos[1]+self.cellSize-eyeSize-8, eyeSize, eyeSize))

            pygame.draw.rect(self.mapSurface, BLACK, (pos[0]+self.cellSize-eyeSize-8, pos[1]+5, eyeSize, eyeSize), 2)
            pygame.draw.rect(self.mapSurface, BLACK, (pos[0]+self.cellSize-eyeSize-8, pos[1]+self.cellSize-eyeSize-8, eyeSize, eyeSize), 2)


    def DrawFinishBlock(self, pos, customColor = None):
        halfCell = int(self.cellSize/2)-1

        # Draw rects to achieve flag pattern look
        pygame.draw.rect(self.mapSurface, self.finishColor, (pos[0], pos[1], halfCell, halfCell))
        pygame.draw.rect(self.mapSurface, self.finishColor, (pos[0]+halfCell, pos[1]+halfCell, halfCell, halfCell))

        # Draw black border
        pygame.draw.rect(self.mapSurface, self.finishColor, (pos[0], pos[1], self.cellSize-2, self.cellSize-2),2)

        # Print finish marker text in edit mode
        # (Finish cell is always drawn in game)
        if self.editMode == True:
            self.finishMarkerText.SetPos((int(pos[0] + (self.cellSize/2)-self.finishMarkerText.GetWidth()/2)-1, pos[1]+(self.cellSize/2)-8))
            self.finishMarkerText.Draw()

    def DrawWallBlock(self, pos, customColor = None):
        pygame.draw.rect(self.mapSurface, self.wallColor, (pos[0], pos[1], self.cellSize-1, self.cellSize-1))
        pygame.draw.rect(self.mapSurface, BLACK, (pos[0], pos[1], self.cellSize-1, self.cellSize-1), 1)

    def DrawDoorBlock(self, pos, dID):
        # If it is a doorblock draw the correct
        # colored door based on Cell id
        halfCell = int(self.cellSize/2)-1
        holeSize = int(halfCell/2)

        # Fill the cell with door color
        pygame.draw.rect(self.mapSurface, self.doorColors[dID], (pos[0], pos[1], self.cellSize-1, self.cellSize-1))

        # Draw black border
        pygame.draw.rect(self.mapSurface, BLACK, (pos[0], pos[1], self.cellSize-2, self.cellSize-2),2)

        # Keyhole
        pygame.draw.circle(self.mapSurface, BLACK, (pos[0]+halfCell, pos[1]+halfCell), holeSize)

        # Keyhole bottom
        pygame.draw.rect(self.mapSurface, BLACK, (pos[0]+halfCell-3, pos[1]+halfCell+3, 6, 9))

    def DrawKey(self, pos, kID, customColor = None):
        halfCell = int(self.cellSize/2)-1
        ringSize = int(halfCell/2)
        stemWidth = 4
        if not customColor == None:
            pygame.draw.rect(self.mapSurface, GREY, (pos[0] + halfCell - int(stemWidth/2), pos[1]+ringSize*2, stemWidth, halfCell))
            pygame.draw.rect(self.mapSurface, GREY, (pos[0] + halfCell - int(stemWidth/2)-3, pos[1]+self.cellSize-8, stemWidth-1, (halfCell/2)-5))
            pygame.draw.rect(self.mapSurface, GREY, (pos[0] + halfCell - int(stemWidth/2)-3, pos[1]+self.cellSize-5, stemWidth-1, (halfCell/2)-5))
            pygame.draw.circle(self.mapSurface, customColor, (pos[0]+halfCell, pos[1]+ringSize+2), ringSize+1, 3)
        else:
            pygame.draw.rect(self.mapSurface, GREY, (pos[0] + halfCell - int(stemWidth/2), pos[1]+ringSize*2, stemWidth, halfCell))
            pygame.draw.rect(self.mapSurface, GREY, (pos[0] + halfCell - int(stemWidth/2)-3, pos[1]+self.cellSize-8, stemWidth-1, (halfCell/2)-5))
            pygame.draw.rect(self.mapSurface, GREY, (pos[0] + halfCell - int(stemWidth/2)-3, pos[1]+self.cellSize-5, stemWidth-1, (halfCell/2)-5))
            pygame.draw.circle(self.mapSurface, self.doorColors[kID], (pos[0]+halfCell, pos[1]+ringSize+2), ringSize+1, 3)

    def DrawPortalBlock(self, pos, pID, portalEnd = False):
        #pygame.draw.rect(self.mapSurface, LAVENDAR, (cellPos[0], cellPos[1], self.cellSize-1, self.cellSize-1),1)
        halfCell = int(self.cellSize/2)-1

        for n in range(4):
            pygame.draw.circle(self.mapSurface, self.portalColors[pID], (pos[0]+halfCell, pos[1]+halfCell),4*n+1,1)

        pygame.draw.circle(self.mapSurface, self.portalColors[pID], (pos[0] + 5, pos[1]+5), 4, 2)
        pygame.draw.circle(self.mapSurface, self.portalColors[pID], (pos[0] + self.cellSize-7, pos[1]+5), 4, 2)

        pygame.draw.circle(self.mapSurface, self.portalColors[pID], (pos[0]+5, pos[1]+self.cellSize-7), 4, 2)
        pygame.draw.circle(self.mapSurface, self.portalColors[pID], (pos[0]+self.cellSize-7, pos[1]+self.cellSize-7), 4, 2)

        if not portalEnd:
            # Draw a I for portal beginnings
            if self.editMode == True:
                pygame.draw.rect(self.mapSurface, BLACK, (pos[0]+halfCell-2, pos[1]+int(halfCell/2), 4, halfCell))

        elif portalEnd == True:
            # Draw a II for portal beginnings
            if self.editMode == True:
                pygame.draw.rect(self.mapSurface, BLACK, (pos[0]+halfCell-5, pos[1]+int(halfCell/2), 4, halfCell))
                pygame.draw.rect(self.mapSurface, BLACK, (pos[0]+halfCell+1, pos[1]+int(halfCell/2), 4, halfCell))



    def Draw(self):
        dw = self.cellSize*self.rows
        dh = self.cellSize*self.cols
        UL = (0, -1)     # Upper left
        UR = (dw-1, -1)  # Upper right
        BR = (dw-1, dh-1) # Bottom right
        BL = (0, dh-1)    # Bottom left

        # Go through all cells and draw
        # the appropriate blockType
        for row in self.cellsNew:
            for cell in row:
                cellPos = self.GetRealPoint(cell.gridX, cell.gridY)

                #STARTBLOCK
                if cell.blockType == STARTBLOCK and self.editMode == True:
                    self.DrawPlayerBlock(cellPos, self.startDirection)

                #FINISHBLOCK
                if cell.blockType == FINISHBLOCK:
                    self.DrawFinishBlock(cellPos)

                #WALLBLOCK
                if cell.blockType == WALLBLOCK:
                    self.DrawWallBlock(cellPos)

                #DOORBLOCK
                if cell.blockType == DOORBLOCK:
                    self.DrawDoorBlock(cellPos, cell.id)

                # KEYBLOCK
                if cell.blockType == KEYBLOCK:
                    # If it is a keyblock draw the correct
                    # colored key based on Cell id
                    self.DrawKey(cellPos, cell.id)

                # PORTALBEGIN
                if cell.blockType == PORTALBEGIN:
                    # Same for portal beginnings
                    self.DrawPortalBlock(cellPos, cell.id)


                # PORTALEND
                if cell.blockType == PORTALEND:
                    # and ends
                    self.DrawPortalBlock(cellPos, cell.id, portalEnd = True)


        # Draw grid border
        pygame.draw.line(self.mapSurface, GRIDCOLOR, (UL), (UR))
        pygame.draw.line(self.mapSurface, GRIDCOLOR, (UR), (BR))
        pygame.draw.line(self.mapSurface, GRIDCOLOR, (BR), (BL))
        pygame.draw.line(self.mapSurface, GRIDCOLOR, (BL), (UL))

        # If edit mode is enabled
        # Draw editor components
        if self.editMode == True:
            self.DrawEditor()

    def DrawEditor(self):
        dw = self.cellSize*self.rows
        dh = self.cellSize*self.cols
        UL = (0, 0)
        UR = (dw-1, 0)
        BR = (dw-1, dh-1)
        BL = (0, dh-1)

        # Draw the actual grid if editMode is enabled
        for r in range(self.rows):
            pygame.draw.line(self.mapSurface, GRIDCOLOR, (r*self.cellSize-1, 0), (r*self.cellSize-1, dh))

        for c in range(self.cols):
            pygame.draw.line(self.mapSurface, GRIDCOLOR, (0, c*self.cellSize-1), (dw, c*self.cellSize-1))



        # Highlight cell under the cursor
        mousePos = pygame.mouse.get_pos()

        if mousePos[1] < self.mapHeight:
            if self.editSelect == 0: # Start Point
                pygame.draw.rect(self.mapSurface, self.playerColor, (self.mouseMapPos[0]*self.cellSize, self.mouseMapPos[1]*self.cellSize, self.cellSize-2, self.cellSize-2), 2)
                pygame.draw.rect(self.mapSurface, BLACK, (self.mouseMapPos[0]*self.cellSize+2, self.mouseMapPos[1]*self.cellSize+2, self.cellSize-5, self.cellSize-5), 1)

            elif self.editSelect == 1: # Finish Point
                pygame.draw.rect(self.mapSurface, self.finishColor, (self.mouseMapPos[0]*self.cellSize, self.mouseMapPos[1]*self.cellSize, self.cellSize-2, self.cellSize-2), 2)
                pygame.draw.rect(self.mapSurface, BLACK, (self.mouseMapPos[0]*self.cellSize+2, self.mouseMapPos[1]*self.cellSize+2, self.cellSize-5, self.cellSize-5), 1)

            elif self.editSelect == 2: # Walls
                pygame.draw.rect(self.mapSurface, self.wallColor, (self.mouseMapPos[0]*self.cellSize, self.mouseMapPos[1]*self.cellSize, self.cellSize-2, self.cellSize-2), 2)
                pygame.draw.rect(self.mapSurface, BLACK, (self.mouseMapPos[0]*self.cellSize+2, self.mouseMapPos[1]*self.cellSize+2, self.cellSize-5, self.cellSize-5), 1)

            elif self.editSelect == 3: # Doors
                pygame.draw.rect(self.mapSurface, self.doorColors[self.eCurrentDoorIndex], (self.mouseMapPos[0]*self.cellSize, self.mouseMapPos[1]*self.cellSize, self.cellSize-2, self.cellSize-2), 2)
                pygame.draw.rect(self.mapSurface, BLACK, (self.mouseMapPos[0]*self.cellSize+2, self.mouseMapPos[1]*self.cellSize+2, self.cellSize-5, self.cellSize-5), 1)

            elif self.editSelect == 4: # Keys
                pygame.draw.rect(self.mapSurface, self.doorColors[self.eCurrentKeyIndex], (self.mouseMapPos[0]*self.cellSize, self.mouseMapPos[1]*self.cellSize, self.cellSize-2, self.cellSize-2), 2)
                pygame.draw.rect(self.mapSurface, BLACK, (self.mouseMapPos[0]*self.cellSize+2, self.mouseMapPos[1]*self.cellSize+2, self.cellSize-5, self.cellSize-5), 1)

            elif self.editSelect == 5: # Portal Begins
                pygame.draw.rect(self.mapSurface, self.portalColors[self.eCurrentPortalBeginIndex], (self.mouseMapPos[0]*self.cellSize, self.mouseMapPos[1]*self.cellSize, self.cellSize-2, self.cellSize-2), 2)
                pygame.draw.rect(self.mapSurface, BLACK, (self.mouseMapPos[0]*self.cellSize+2, self.mouseMapPos[1]*self.cellSize+2, self.cellSize-5, self.cellSize-5), 1)

            elif self.editSelect == 6: # Portal Ends
                pygame.draw.rect(self.mapSurface, self.portalColors[self.eCurrentPortalEndIndex], (self.mouseMapPos[0]*self.cellSize, self.mouseMapPos[1]*self.cellSize, self.cellSize-2, self.cellSize-2), 2)
                pygame.draw.rect(self.mapSurface, BLACK, (self.mouseMapPos[0]*self.cellSize+2, self.mouseMapPos[1]*self.cellSize+2, self.cellSize-5, self.cellSize-5), 1)

    def ListIndices(self):
        print()
        print("Door index: ", self.eCurrentDoorIndex)
        print("Key index: ", self.eCurrentKeyIndex)
        print("Portal Begin index: ", self.eCurrentPortalBeginIndex)
        print("Portal End index: ", self.eCurrentPortalEndIndex)

# This is the official file loader for grid maps
def LoadMap(fPath, dSurf):
    fixedPath = Path(fPath)
    print()
    print("Loading: ", fixedPath)

    with open(fixedPath, 'rt', encoding='utf-8', newline='\n') as f:
        start = (-1, -1)
        finish = (-5, -5)
        rowOfCells  = []
        gCells = []
        gCellsNew = []
        newCell = Cell(EMPTYBLOCK)
        gDoorColors = defaultDoorColors
        gPortalColors = defaultPortalColors
        gWallColor = BLACK
        gPlayerColor = LIGHTBLUE
        gFinishColor = GREEN

        wallCount = 0
        doorIndex = 0
        portalBeginIndex = 0
        portalEndIndex = 0
        keyIndex = 0
        colorSection = False
        startDirection = 0
        cellReader = enumerate(csv.reader(f))

        gx = 0
        gy = 0
        rCount = 0
        cCount = 0

        gScores = []
        scoreLine = ''

        for r, row in cellReader:
            gx = 0
            for c in row:
                gy = r

                if c == 'h':
                    digitCount = len(c)
                    # Load in the maps highscore list
                    print(row[1])
                    floatedScore = float(row[1])
                    roundedScore = round(floatedScore, 3)
                    gScores.append(roundedScore)
                    colorSection = True

                elif c == 'c':
                    colorSection = True

                # If this line defines a color, determine what
                # blocks color it defines
                if colorSection == True:
                    if row[1] == "Wall":
                        cRed = float(row[2])
                        cGreen = float(row[3])
                        cBlue = float(row[4])
                        newColor = (cRed, cGreen, cBlue)
                        gWallColor = newColor
                        #print("Wall color: ", end = '')
                        #print("R:"+str(cRed), "| G:"+str(cGreen), "| B:"+str(cBlue))

                    elif row[1] == "Player":
                        cRed = float(row[2])
                        cGreen = float(row[3])
                        cBlue = float(row[4])
                        newColor = (cRed, cGreen, cBlue)
                        gPlayerColor = newColor
                        #print("Player color: ", end = '')
                        #print("R:"+str(cRed), "| G:"+str(cGreen), "| B:"+str(cBlue))

                    elif row[1] == "Finish":
                        cRed = float(row[2])
                        cGreen = float(row[3])
                        cBlue = float(row[4])
                        newColor = (cRed, cGreen, cBlue)
                        gFinishColor = newColor
                        #print("Finish color: ", end = '')
                        #print("R:"+str(cRed), "| G:"+str(cGreen), "| B:"+str(cBlue))

                    elif row[1] == "Door":
                        cRed = float(row[3])
                        cGreen = float(row[4])
                        cBlue = float(row[5])
                        newColor = (cRed, cGreen, cBlue)
                        doorColorID = int(row[2])

                        # If the door ID is greater than the length of
                        # the list of door colors, append as  a new color

                        if doorColorID >= len(gDoorColors):
                            gDoorColors.append(newColor)
                        else:
                            gDoorColors[doorColorID] = newColor
                        #print("Door ", doorColorID, "color: ", end = '')
                        #print("R:"+str(cRed), "| G:"+str(cGreen), "| B:"+str(cBlue))

                    elif row[1] == "Portal":
                        cRed = float(row[3])
                        cGreen = float(row[4])
                        cBlue = float(row[5])
                        newColor = (cRed, cGreen, cBlue)
                        portalColorID = int(row[2])

                        if portalColorID >= len(gPortalColors):
                            gPortalColors.append(newColor)
                        else:
                            gPortalColors[portalColorID] = newColor

                        #print("Portal ", portalColorID, "color: ", end = '')
                        #print("R:"+str(cRed), "| G:"+str(cGreen), "| B:"+str(cBlue))

                # If this line isn't a color section, determine
                # What the block type is and append to cells grid
                if not colorSection:
                    if c[0] == "S":
                        startDirection = int(c[1])
                        if startDirection > 3:
                            startDirection = 0

                        elif startDirection < 0:
                            startDirection = 3

                        newCell = Cell(STARTBLOCK, gx, gy, startDirection)
                        gCells.append(newCell)
                        rowOfCells.append(newCell)
                        start = (gx,gy)
                        # print(STARTBLOCK, end = ' | ')

                    elif c[0] == "D":

                        digitCount = len(c)
                        cidStr = ''

                        # Append the following digits after 'D' to get
                        # the full door ID
                        for d in range(1, digitCount):
                            cidStr += c[d]

                        newCell = Cell(DOORBLOCK, gx, gy, int(cidStr))
                        gCells.append(newCell)
                        rowOfCells.append(newCell)
                        doorIndex += 1
                        # print(DOORBLOCK, newCell.id, end = ' | ')

                    elif c[0] == "K":
                        digitCount = len(c)
                        cidStr = ''

                        # Append the following digits after 'K' to get
                        # the full key ID
                        for d in range(1, digitCount):
                            cidStr += c[d]

                        newCell = Cell(KEYBLOCK, gx, gy, int(cidStr))
                        gCells.append(newCell)
                        rowOfCells.append(newCell)

                        keyIndex += 1
                        # print(KEYBLOCK, newCell.id, end = ' | ')

                    elif c[0] == "p":
                        digitCount = len(c)
                        cidStr = ''

                        # Append the following digits after 'K' to get
                        # the full key ID
                        for d in range(1, digitCount):
                            cidStr += c[d]

                        newCell = Cell(PORTALBEGIN, gx, gy, int(cidStr))
                        gCells.append(newCell)
                        rowOfCells.append(newCell)

                        portalBeginIndex += 1
                        # print(PORTALBEGIN, newCell.id, end = ' | ')

                    elif c[0] == "P":
                        digitCount = len(c)
                        cidStr = ''

                        # Append the following digits after 'K' to get
                        # the full key ID
                        for d in range(1, digitCount):
                            cidStr += c[d]

                        newCell = Cell(PORTALEND, gx, gy, int(cidStr))

                        gCells.append(newCell)
                        rowOfCells.append(newCell)

                        portalEndIndex += 1
                        # print(PORTALEND, newCell.id, end = ' | ')

                    elif c == '##':
                        newCell = Cell(EMPTYBLOCK, gx, gy)
                        gCells.append(newCell)
                        rowOfCells.append(newCell)
                        # print(EMPTYBLOCK, end = ' | ')

                    elif c == 'WW':
                        newCell = Cell(WALLBLOCK, gx, gy)
                        gCells.append(newCell)
                        rowOfCells.append(newCell)
                        wallCount += 1
                        # print(WALLBLOCK, end = ' | ')

                    elif c == 'FF':
                        newCell = Cell(FINISHBLOCK, gx, gy)
                        gCells.append(newCell)
                        rowOfCells.append(newCell)
                        finish = (gx,gy)
                        # print(FINISHBLOCK, end = ' | ')


                    # Increase cell x index
                    gx += 1

            # Read out the contents of the file
            # for verification
            if not colorSection:
                cCount +=1
                rCount = gx
                gCellsNew.append(rowOfCells)
                scoreLine = ''
                rowOfCells = []

        print("Found ", wallCount, "walls.")
        print("Map Size: (", str(rCount) + "," + str(cCount),")")


        # Create the new map and occupy it
        # with new cells
        newMap = Map(dSurf, rCount, cCount, dCellsize)
        newMap.cellsNew = gCellsNew


        newMap.startCell = gCellsNew[start[1]][start[0]]
        newMap.startCell.id = newMap.startDirection
        if finish[0] > 0:
            newMap.finishCell = gCellsNew[finish[1]][finish[0]]
        else:
            newMap.finishCell = None

        newMap.doorColors = gDoorColors
        newMap.portalColors = gPortalColors
        newMap.wallColor = gWallColor
        newMap.playerColor = gPlayerColor
        newMap.finishColor = gFinishColor

        newMap.eTotalDoors = doorIndex
        newMap.eTotalKeys = keyIndex
        newMap.eTotalPortalBegins = portalBeginIndex
        newMap.eTotalPortalEnds = portalEndIndex

        newMap.eCurrentDoorIndex = doorIndex
        newMap.eCurrentKeyIndex = keyIndex
        newMap.eCurrentPortalBeginIndex = portalBeginIndex
        newMap.eCurrentPortalEndIndex = portalEndIndex

        newMap.startDirection = startDirection
        newMap.scores = gScores
        if len(gScores) > 0:
            newMap.currentBest = min(gScores)
        print("\nCurrent Best:", newMap.currentBest)
        newMap.filePath = fixedPath
        newMap.editMode = False
        newMap.ListIndices()
        return newMap



def AskLoadMap(dSurf):
    root = tkinter.Tk()
    fTypes = [("Map Files", "*.gmf")]
    mPath = FD.askopenfilename(initialdir = mapDir, filetypes = fTypes)
    root.destroy()

    if mPath  != ():
        fixedPath = Path(mPath)
        newMap = LoadMap(mPath, dSurf)
        return newMap
    else:
        return None