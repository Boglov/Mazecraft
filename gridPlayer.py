import pygame
import sys
from gridMap import *
from pygame.locals import *

sfxDir = os.path.dirname(os.path.realpath(__file__)) + "/data/sfx/"

getKeySound = pygame.mixer.Sound(sfxDir + "getkey.wav")
unlockSound = pygame.mixer.Sound(sfxDir + "unlock.wav")
portalSound = pygame.mixer.Sound(sfxDir + "portal.wav")
finishSound = pygame.mixer.Sound(sfxDir + "fin.wav")
denySound = pygame.mixer.Sound(sfxDir + "deny.wav")

def SetSfxVolume(newVol):
    realVol = newVol/100
    #print("Real sfx vol:%f"%realVol)
    getKeySound.set_volume(realVol)
    unlockSound.set_volume(realVol)
    portalSound.set_volume(realVol)
    finishSound.set_volume(realVol)
    denySound.set_volume(realVol)

class Key:
    def __init__(self, kID):
        self.isForDoor = kID

class Player:
    def __init__(self, dSurf, g):
        self.grid = g
        self.gridX = 2
        self.gridY = 2
        self.realPos = self.grid.GetRealPoint(self.gridX, self.gridY)

        self.keys = []
        self.mapCompleted = False
        self.displaySurf = dSurf
        self.facing = 0
        self.speed = 1
        self.stepCounter = -3

    def SetPos(self, newPos):
        # Ensure the new position is within the bounds
        # of the map

        tx = clip(newPos[0], 0, self.grid.rows-1)
        ty = clip(newPos[1], 0, self.grid.cols-1)

        # Set player position using grid coordinates
        isWall = self.grid.CheckFor(WALLBLOCK, tx, ty)
        isDoor = self.grid.CheckFor(DOORBLOCK, tx, ty)
        isKey = self.grid.CheckFor(KEYBLOCK, tx, ty)
        isPortalBegin = self.grid.CheckFor(PORTALBEGIN, tx, ty)
        isPortalEnd = self.grid.CheckFor(PORTALEND, tx, ty)


        # Check if the portal has an end counterpart
        # and if so teleport to it
        if isPortalBegin:
            portalID = self.grid.GetBlockID(tx,ty)
            endCheck = self.grid.GetPortalEnd(portalID)

            if endCheck != None:
                portalSound.play()
                pEnd = endCheck

                self.gridX = pEnd[0]
                self.gridY = pEnd[1]
                self.realPos = self.grid.GetRealPoint(self.gridX, self.gridY)
            else:
                self.gridX = tx
                self.gridY = ty
                self.realPos = self.grid.GetRealPoint(tx, ty)
            return

        # Check if the portal has a begin counterpart
        # and if so teleport to it
        elif isPortalEnd:
            portalID = self.grid.GetBlockID(tx,ty)
            beginCheck = self.grid.GetPortalBegin(portalID)

            if beginCheck != None:
                portalSound.play()

                pBegin = beginCheck
                self.gridX = pBegin[0]
                self.gridY = pBegin[1]
                self.realPos = self.grid.GetRealPoint(self.gridX, self.gridY)
            else:
                self.gridX = tx
                self.gridY = ty
                self.realPos = self.grid.GetRealPoint(tx, ty)
            return

        elif isKey:
            getKeySound.play()
            keyID = self.grid.GetBlockID(tx,ty)
            newKey = Key(keyID)
            self.keys.append(newKey)
            self.grid.ClearBlock(tx, ty)
            print("You obtained a key to Door", keyID,"!")

        elif isDoor:
            doorID = self.grid.GetBlockID(tx,ty)
            if self.HasKey(doorID):
                unlockSound.play()
                self.grid.ClearBlock(tx, ty)
                self.UseKey(doorID)
                print("You open door", str(doorID), "with a key!")

            else:
                denySound.play()
                print("You need the key", str(doorID)+"to open that!")

        if not isWall and not isDoor:
            self.gridX = tx
            self.gridY = ty
            self.realPos = self.grid.GetRealPoint(tx, ty)
            if self.stepCounter < 1:
                self.stepCounter += 1

        # Check if current position is the finish cell
        cPos = (tx, ty)
        if not self.grid.finishCell == None:
            if cPos == (self.grid.finishCell.gridX, self.grid.finishCell.gridY):
                finishSound.play()
                print("Success")
                self.mapCompleted = True

    def UseKey(self, kID):
        keyFound = False
        thisKey = 0
        for k in self.keys:
            if k.isForDoor == kID:
                self.keys.pop(thisKey)
                keyFound = True
                break
            thisKey += 1

    def HasKey(self, kID):
        for k in self.keys:
            if k.isForDoor == kID:
                return True
        return False

    def UpdateMap(self, nMap):
        self.grid = nMap
        if nMap.startCell.gridX >= 0:
            startCell = nMap.startCell
            self.SetPos((startCell.gridX, startCell.gridY))
        self.facing = self.grid.startDirection
        self.keys = []
        self.stepCounter = -1
        self.mapCompleted = False

    def Draw(self):
        if not self.grid.startCell.gridX < 0:
            self.grid.DrawPlayerBlock(self.realPos, self.facing)


    def Move(self, x, y):
        if y < 0:
            self.facing = 3

        elif y > 0:
            self.facing = 1

        elif x < 0:
            self.facing = 2

        elif x > 0:
            self.facing = 0


        nx = self.gridX + x
        ny = self.gridY + y

        self.SetPos((int(nx), int(ny)))


    def HandleShiftInput(self, kState):
        if kState[pygame.K_LSHIFT] or kState[pygame.K_SPACE]:
            if kState[pygame.K_w] or kState[pygame.K_UP]:
                self.Move(0, -self.speed)
            elif kState[pygame.K_s] or kState[pygame.K_DOWN]:
                self.Move(0, self.speed)
            elif kState[pygame.K_a] or kState[pygame.K_LEFT]:
                self.Move(-self.speed, 0)
            elif kState[pygame.K_d] or kState[pygame.K_RIGHT]:
                self.Move(self.speed, 0)

    def HandleNormalInput(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.Move(0, -self.speed)

            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.Move(0, self.speed)

            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.Move(-self.speed, 0)

            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.Move(self.speed, 0)