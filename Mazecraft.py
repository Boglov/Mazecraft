# Maze Daze
# written by Zachery Visger
# Just have fun!

import pygame
import sys
import os
import gridMap
import gridPlayer
import time
import webbrowser
import csv
from gxElements import *
import gxFiles as gxF

from gxColors import *
from tkinter import colorchooser
from tkinter import Tk

if False:
    import pygame._view

## Specify the game states for
# better claritye
MAINMENUSTATE = 0
INGAMESTATE = 1
EDITORSTATE = 2

## CURRENTSTATE defines which statee
# loop should currently be executed
CURRENTSTATE = MAINMENUSTATE

# Possibly implement sub states for panels
# and sub menus
SUBSTATE = 0

#WINDOWX = 300
#WINDOWY = 100
#os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (WINDOWX, WINDOWY)

#cfgFile = gridMap.homeDir + "/mdConfig.cfg"

currentMap = gridMap.levelDir + "Level1.gmf"
lastEditedMap = gridMap.mapDir + "untitled.gmf"
cfgFile = gridMap.homeDir + "/config.cfg"
pygame.init()

# Create a list to store config data which will
# persist through sessions. To be saved upon
# changes made
CFGDATA = []
CFGDATA.append(['musicVol', 0])
CFGDATA.append(['sfxVol', 0])


EXITED = 0
GAMETITLE = "Mazecraft"

UIBUFFER = 100
DWIDTH = 100
DHEIGHT = 100
UIbegin_Y = DHEIGHT - UIBUFFER
DSURF = pygame.display.set_mode((DWIDTH, DHEIGHT))

pygame.display.set_caption("Map Editor")

FPS = 60
FPSCLOCK = pygame.time.Clock()

levelStartTime = time.time()
levelFinishTime = time.time()
levelTime = 0

# Specific element colors
BGCOLOR = WHITE
MENUBGCOLOR = WHITE


currentMusic = pygame.mixer.music.load(gridPlayer.sfxDir+'music1.mp2')
inGameMusic = pygame.mixer.music.load(gridPlayer.sfxDir+'mainmenu.wav')

musicVolume = 100
sfxVolume = 100

def SetMusicVolume(v):
    realVol = v/100
    # print("Real V:%f"%realVol)
    pygame.mixer.music.set_volume(realVol)

def SetWindowSize(dW, dH):
    if dW > 0 and dH > 0:
        global DWIDTH, DHEIGHT, UIbegin_Y, UIBUFFER
        DWIDTH = dW
        DHEIGHT = dH
        UIbegin_Y = dH-UIBUFFER
        DSURF = pygame.display.set_mode((DWIDTH, DHEIGHT))

def FitWindowToMap(nMap, includeUI=True):
    if includeUI == True:
        SetWindowSize(nMap.mapWidth, nMap.totalHeight)
    elif includeUI == False:
        SetWindowSize(nMap.mapWidth, nMap.mapHeight)

def PlayMenuMusic():
    currentMusic = pygame.mixer.music.load(gridPlayer.sfxDir+'music1.mp2')
    pygame.mixer.music.play(-1)

def PlayInGameMusic():
    currentMusic = pygame.mixer.music.load(gridPlayer.sfxDir+'mainmenu.wav')
    pygame.mixer.music.play(-1)

def StartLevelTimer():
    levelStartTime = time.time()

def ResetLevelTimer():
    global levelStartTime, levelFinishTime, levelTime
    levelStartTime = time.time()
    levelFinishTime = time.time()

def StopLevelTimer():
    global levelStartTime, levelFinishTime, levelTime
    levelFinishTime = time.time()
    levelTime = round(levelFinishTime - levelStartTime, 2)
    return levelTime

def SaveLevelTime():
    gameMap.AddScore(levelTime)

def CheckForLevel(lNumber):
    global gameMap
    nextLevelPath = gridMap.levelDir + "Level" + str(lNumber) + ".gmf"

    if os.path.isfile(nextLevelPath):
        return nextLevelPath
    else:
        return None

def GetAllLevelPaths():
    looking = True
    levelIndex = 1
    levelPaths = []

    while looking:
        checkPath = CheckForLevel(levelIndex)
        if checkPath != None:
            levelPaths.append(checkPath)
            levelIndex += 1
        else:
            looking = False

    return levelPaths


### Initialize all UI and map data
##

# Initialize the game map
gameMap = gridMap.LoadMap(gridMap.menuMapDir + "MainMenuMap.gmf", DSURF)

# Initialize the player
player = gridPlayer.Player(DSURF, gameMap)

# Set the window size to match
# the size of the game map
FitWindowToMap(gameMap, False)

# This GX_Note is used for pop up notes
# to inform the player of important information
# such as changes to files
n_Notifier = GX_Note(DSURF, (0,0))

### Main menu UI elements
txt_MainTitle = GX_Text(DSURF, GAMETITLE, BLACK, (0,0), 30)

btn_mPlay = GX_Button(DSURF, "Play", (0,0))
btn_mPlay.SetFillcolor(WHITE)

btn_mLevelSelect = GX_Button(DSURF, "Level Select", (0,0))
btn_mLevelSelect.SetFillcolor(WHITE)

btn_mEditMode = GX_Button(DSURF, "Map Editor", (0,0))
btn_mEditMode.SetFillcolor(WHITE)

btn_mOptions = GX_Button(DSURF, "Options", (0,0))
btn_mOptions.SetFillcolor(WHITE)

btn_mCredits = GX_Button(DSURF, "Credits", (0,0))
btn_mCredits.SetFillcolor(WHITE)

btn_mExit = GX_Button(DSURF, "Exit Game", (0,0))

## Begin decorative menu keys initializaton
# Initialize the position and color
# of the decorative keys on the main menu
menuKeys_yPositions = []
menuKeys_yPositions.append(0)
menuKeys_yPositions.append(-100)
menuKeys_yPositions.append(-200)
menuKeys_yPositions.append(-300)
mKeySpeed = .4

menuKeyColors = []
menuKeyColors.append(GetRandomColor())
menuKeyColors.append(GetRandomColor())
menuKeyColors.append(GetRandomColor())
menuKeyColors.append(GetRandomColor())
menuKeyColors.append(GetRandomColor())
menuKeyColors.append(GetRandomColor())
menuKeyColors.append(GetRandomColor())
menuKeyColors.append(GetRandomColor())


## Begin Level Select panel initialization
# Initialize the actual Level Select panel

pnl_mLevelSelect = GX_Panel(DSURF, (0,110), "Level Select")
pnl_mLevelSelect.centeredElements = False
pnl_mLevelSelect.hCentered = True
pnl_mLevelSelect.centered = False
pnl_mLevelSelect.titleIsButton = True
pnl_mLevelSelect.colWidth = 50

# Create an initial list of the levels
# within the Levels folder
levelPaths = GetAllLevelPaths()
numOfLevels = len(levelPaths)

# Add all the found levels to the level
# select panel
for lvl in range(numOfLevels):
    pnl_mLevelSelect.AddElement(UIBUTTON, "L: " + str(lvl+1))

## Begin Map Size selection panel initialization
# Initialize the actual map size selection panel
pnl_mMapSizes = GX_Panel(DSURF, (0, 150), "New Map Size")
pnl_mMapSizes.hCentered = True
pnl_mMapSizes.centered = False
pnl_mMapSizes.centeredElements = False
pnl_mMapSizes.titleIsButton = True
pnl_mMapSizes.rowLimit = 4
pnl_mMapSizes.AddElement(UIBUTTON, "10x10")
pnl_mMapSizes.AddElement(UIBUTTON, "15x15")
pnl_mMapSizes.AddElement(UIBUTTON, "20x20")
pnl_mMapSizes.AddElement(UIBUTTON, "25x25")
pnl_mMapSizes.AddElement(UIBUTTON, "15x10")
pnl_mMapSizes.AddElement(UIBUTTON, "20x15")
pnl_mMapSizes.AddElement(UIBUTTON, "25x20")
pnl_mMapSizes.AddElement(UIBUTTON, "30x25")

pnl_mMapSizes.AddElement(UIBUTTON, "Load")
pnl_mMapSizes.AddElement(UIBUTTON, "Continue")
# pnl_mMapSizes.AddElement(UIBUTTON, "Last Edited")

## Begin Options panel initialization
# Initialize the options panel
# and all its elements
pnl_mOptions = GX_Panel(DSURF, (0,190), "Options")
pnl_mOptions.centered = False
pnl_mOptions.hCentered = True
pnl_mOptions.titleIsButton = True

pnl_mOptions.AddElement(UITEXT, "Music Volume")
pnl_mOptions.AddBlank()
pnl_mOptions.AddElement(UISLIDER, " ")
pnl_mOptions.AddElement(UITEXT, "SFX Volume")
pnl_mOptions.AddBlank()
pnl_mOptions.AddElement(UISLIDER, " ")
pnl_mOptions.AddElement(UIBUTTON, "Clear Highscores")

## Begin Credits panel initialization
# Initialize the credits panel and all
# of it's elements
pnl_mCredits = GX_Panel(DSURF, (0,0), "Credits")
pnl_mCredits.AddElement(UITEXT, "Default in-game music track:")
pnl_mCredits.AddElement(UITEXT, '"Game-Menu"')
pnl_mCredits.AddElement(UITEXT, "By Eric Matyas")
pnl_mCredits.AddElement(UIBUTTON, "www.soundimage.org")
pnl_mCredits.AddBlank()
pnl_mCredits.AddElement(UITEXT, "Sound effects obtained from")
pnl_mCredits.AddElement(UIBUTTON, "https://www.zapsplat.com")
pnl_mCredits.AddBlank()
pnl_mCredits.AddElement(UITEXT, "Game design, Graphics, and Code")
pnl_mCredits.AddElement(UITEXT, "By Zachery Visger")
pnl_mCredits.AddElement(UITEXT, "")
pnl_mCredits.hasBackButton = True

# Set the names in the credits panel to green
pnl_mCredits.SetTextColor(1, BLUE)
pnl_mCredits.SetTextColor(2, GREEN)
pnl_mCredits.SetTextColor(5, GREEN)

pnl_mCredits.UpdateSurface()

### Editor UI elements
#txt_EditorTitle = GX_Text(DSURF, "Editor", BLACK, (0, UIbegin_Y))

btn_Wall = GX_Button(DSURF, "Wall")
btn_Wall.SetFillcolor(gameMap.wallColor)

btn_Door = GX_Button(DSURF, "Door")
btn_Door.SetFillcolor(gameMap.doorColors[0])

btn_PortBegin = GX_Button(DSURF, "Port S")
btn_PortBegin.SetFillcolor(gameMap.doorColors[1])

btn_Key = GX_Button(DSURF, "Key")
btn_Key.SetFillcolor(gameMap.doorColors[0])

btn_PortEnd = GX_Button(DSURF, "Port E")
btn_PortEnd.SetFillcolor(gameMap.doorColors[1])

btn_Player = GX_Button(DSURF, "Player")
btn_Player.SetFillcolor(gameMap.playerColor)

btn_FinishPoint = GX_Button(DSURF, "Finish")
btn_FinishPoint.SetFillcolor(gameMap.finishColor)

btn_ColorPicker = GX_Button(DSURF, "Color Picker")

btn_RandColor = GX_Button(DSURF, "Random Color")
btn_AddToLevels = GX_Button(DSURF, "Add to Levels")
btn_Save = GX_Button(DSURF, "Save")

btn_SaveNew = GX_Button(DSURF, "Save As")

btn_Load = GX_Button(DSURF, "Load")

btn_Test = GX_Button(DSURF, "Test")

btn_MainMenu = GX_Button(DSURF, "Main Menu")
####

fk_DoorFlicker = GX_Flicker(DSURF)
fk_KeyFlicker = GX_Flicker(DSURF)
fk_PBeginFlicker = GX_Flicker(DSURF)
fk_PEndFlicker = GX_Flicker(DSURF)

### In game UI elements
txt_InGameTitle = GX_Text(DSURF, "Keys: ", BLACK, (0, UIbegin_Y+10))
txt_LevelTimer = GX_Text(DSURF, "Time: ", BLUE, (0, DHEIGHT-15))
txt_BestTime = GX_Text(DSURF, "BestTime: ", GREEN, (0, DHEIGHT-30))

btn_Edit = GX_Button(DSURF, "Edit", (DWIDTH, DHEIGHT))
btn_Reset = GX_Button(DSURF, "Reset", (0, UIbegin_Y+55))
btn_Reset.fillColor = ORANGERED

## Begin Score panel initialization
pnl_Score = GX_Panel(DSURF, (20,10))
pnl_Score.AddElement(UITEXT, "levelTime")
pnl_Score.AddElement(UITEXT, "bestScore")
pnl_Score.AddElement(UITEXT, "")
pnl_Score.AddElement(UITEXT, "")
pnl_Score.AddElement(UIBUTTON, "Next Level")
pnl_Score.GetButton(0).SetFillcolor(WHITE)

lastEditSelect = 0

# levelCounter keeps track of which level the player is on
levelCounter = 1

# Set the window title to the name of the game
pygame.display.set_caption(GAMETITLE)


# Function to load al the saved config data
# and adjust the settings accordingly
def LoadConfig():
    global CFGDATA, musicVolume, sfxVolume, pnl_mOption
    global cfgFile

    # Load the cfg data into a list
    cD = gxF.LoadFile(cfgFile)

    mV = int(cD[0][1])
    sV = int(cD[1][1])

    musicVolume = mV
    SetMusicVolume(musicVolume)
    print(CFGDATA)

    sfxVolume = sV
    gridPlayer.SetSfxVolume(sfxVolume)

    #print(sVol)
    # Adjust the sliders in Options panel
    # to correctly represent the loaded volume
    pnl_mOptions.GetSlider(0).SetValue(mV)
    pnl_mOptions.GetSlider(1).SetValue(sV)

    print("Music Volume:", mV)
    print("SFX Volume:", sV)

def SaveConfig():
    global CFGDATA, musicVolume, sfxVolume
    CFGDATA[0] = ['musicVol', int(musicVolume)]
    CFGDATA[1] = ['sfxVol', int(sfxVolume)]
    print(CFGDATA)
    gxF.WriteFile(cfgFile, CFGDATA)


## Functions for loading and initializing maps

def UpdateLevelsPanel(levelsPanel):
    global levelPaths, numOfLevels, pnl_mLevelSelect
    # Retrieve a list of all of the level paths
    # including any levels added after game starts
    previousLevelCount = len(levelPaths)
    levelPaths = []
    levelPaths = GetAllLevelPaths()
    numOfLevels = len(levelPaths)

    countDiff = 0

    if(numOfLevels != previousLevelCount):
        countDiff = numOfLevels - previousLevelCount
        print("The number of levels has changed from", previousLevelCount)
        print("to", numOfLevels)
        print("The difference is: ", countDiff, "Levels")

        if numOfLevels > previousLevelCount:
            for bID in range(previousLevelCount, previousLevelCount + countDiff):
                levelsPanel.AddElement(UIBUTTON, "L- " + str(bID+1))
        else:
            for eID in range(abs(countDiff)):
                levelsPanel.PopElement(-1)
    pnl_mLevelselect = levelsPanel

# Function used to import a map and
# update everything that references it
def ImportMap(fPath):
    global gameMap, player, DSURF
    lastEditSelect = gameMap.editSelect
    gameMap = gridMap.LoadMap(str(fPath), DSURF)
    gameMap.editSelect = lastEditSelect

    FitWindowToMap(gameMap)
    player.UpdateMap(gameMap)

    pnl_Score.UpdateSurface()
    pnl_Score.Update()
    pygame.display.set_caption(os.path.splitext(gameMap.filePath.name)[0])

# Function used to initialize a new map
# and update everything that references it
def InitNewMap(r, c, cSize = gridMap.dCellsize):
    global gameMap, player, DSURF
    lastEditSelect = gameMap.editSelect
    gameMap = gridMap.Map(DSURF, r, c, cSize)
    gameMap.editSelect = lastEditSelect
    UpdateEditorColors()

    FitWindowToMap(gameMap)
    player.UpdateMap(gameMap)
    pygame.display.set_caption("untitled")

# Function used to initialize the main menu
# and update everything that references it
def InitMainMenu(startMusic=False):
    global gameMap, DWIDTH, DHEIGHT, UIbegin_Y, levelCounter, n_Notifier
    ImportMap(gridMap.menuMapDir + "MainMenuMap.gmf")
    FitWindowToMap(gameMap, False)
    pnl_mLevelSelect.Hide()
    pnl_mOptions.Hide()
    pnl_mCredits.Hide()
    pnl_mMapSizes.Hide()
    StopLevelTimer()
    LoadConfig()
    levelCounter=1

    if startMusic:
        PlayMenuMusic()

def AskMapToLoad():
    global gameMap, player, CURRENTSTATE, EDITORSTATE, UIbegin_Y
    inMap = gridMap.AskLoadMap(DSURF)
    if inMap != None:
        gameMap = inMap

        gameMap.editMode = True
        FitWindowToMap(gameMap)
        player.UpdateMap(gameMap)
        UpdateEditorColors()

        pygame.display.set_caption(os.path.splitext(gameMap.filePath.name)[0])

        pnl_mLevelSelect.Hide()
        pnl_mOptions.Hide()
        pnl_mCredits.Hide()
        pnl_mMapSizes.Hide()
        pnl_Score.Hide()

        CURRENTSTATE = EDITORSTATE

        n_Notifier.Popup("Loading: " + str(gameMap.filePath.name))
        return True
    return False

# Function used to check if there is a next
# level, if so load it and update all the
# things which reference it. Lastly
# reset the level timers
def LoadLevel(levelNum=1):
    global levelCounter, gameMap, levelTime, CURRENTSTATE

    levelCounter = levelNum
    nextLevelPath = CheckForLevel(levelCounter)

    if nextLevelPath != None:
        # Stop the time and reset it
        StopLevelTimer()
        ImportMap(nextLevelPath)
        player.UpdateMap(gameMap)
        pnl_Score.UpdateSurface()
        ResetLevelTimer()
       #StartLevelTimer()
        print("Next level found.")
        return True
    else:
        # If there are no more levels in the level
        # folder, inform the player
        print("No more levels")
        InitMainMenu(startMusic=True)
        CURRENTSTATE=MAINMENUSTATE
        return False


## Load the saved config data
cfgList = LoadConfig()

## Handle Loops

# Handle main menu UI input
def HandleMainMenuUI():
    global CURRENTSTATE, gameMap, EXITED, levelCounter, levelPaths
    global numOfLevels, musicVolume, sfxVolume
    for event in pygame.event.get():

        # Handle timer events
        n_Notifier.HandleEvents(event)
        
        mvSlider = pnl_mOptions.GetSlider(0)
        svSlider = pnl_mOptions.GetSlider(1)

        mVal = None
        sfxVal = None
        mVal = pnl_mOptions.GetSliderVal(event, 0)
        sfxVal = pnl_mOptions.GetSliderVal(event, 1)

        if not mVal == None:
            musicVolume = mVal
            SetMusicVolume(musicVolume)
            SaveConfig()

        if not sfxVal == None:
            sfxVolume = sfxVal
            gridPlayer.SetSfxVolume(sfxVolume)
            SaveConfig()

        # If the window exit buton is pressed
        if event.type == pygame.QUIT:
            # Exit the game
            EXITED = True

        # If the escape key is pressed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Exit the game
                EXITED = True

        # As long as there are no open panels
        # handle input for main menu buttons
        # If play is clicked
        cPanelIsHiding = pnl_mCredits.IsHiding()
        lsPanelIsHiding = pnl_mLevelSelect.IsHiding()
        oPanelIsHiding = pnl_mOptions.IsHiding()
        msPanelIsHiding = pnl_mMapSizes.IsHiding()

        if  cPanelIsHiding and lsPanelIsHiding and oPanelIsHiding and msPanelIsHiding:
            if(btn_mPlay.OnClick(event)):
                pnl_Score.Hide()
                PlayInGameMusic()
                levelCounter = 1
                LoadLevel(levelCounter)
                pnl_Score.UpdateSurface()
                print(player.stepCounter)
                #ResetLevelTimer()
                #StartLevelTimer()
                CURRENTSTATE = INGAMESTATE

            # If level select is clicked
            if(btn_mLevelSelect.OnClick(event)):
                #pygame.event.clear()
                UpdateLevelsPanel(pnl_mLevelSelect)
                pnl_mLevelSelect.Toggle()

            # If edit mode is clicked
            if(btn_mEditMode.OnClick(event)):
                pnl_mMapSizes.Toggle()
                #ImportMap(lastEditedMap)
                #gameMap.editMode = True
                #CURRENTSTATE = EDITORSTATE

            # If options is clicked
            if(btn_mOptions.OnClick(event)):
                pnl_mOptions.UnHide()

            # If credits is clicked
            if(btn_mCredits.OnClick(event)):
                pygame.event.clear()
                pnl_mCredits.Toggle()

        # If exit is clicked
        if(btn_mExit.OnClick(event)):
            # Exit the game
            EXITED = True

        # Note: GetButtonState() only
        # accepts input while the parent panel
        # is not hidden

        # Begin Level Select panel handling
        pnl_mLevelSelect.HandleTitleButton(event)

        for l in range(numOfLevels):

            # If a level on the levelSelect panel is clicked
            if pnl_mLevelSelect.GetButtonState(event, l):

                # Set the levelCounter to the selected level
                levelCounter = l+1

                # Then load the selected map
                LoadLevel(levelCounter)

                # and start the ingame music track
                PlayInGameMusic()

                # Finally set the game state to the INGAMESTATE
                CURRENTSTATE = INGAMESTATE


        # Begin Map Sizes panel handling
        pnl_mMapSizes.HandleTitleButton(event)

        if not pnl_mMapSizes.IsHiding():
            if(pnl_mMapSizes.GetButtonByName("10x10").OnClick(event)):
                InitNewMap(10, 10)
                gameMap.editMode = True
                CURRENTSTATE = EDITORSTATE

            if(pnl_mMapSizes.GetButtonByName("15x15").OnClick(event)):
                InitNewMap(15, 15)
                gameMap.editMode = True
                CURRENTSTATE = EDITORSTATE

            if(pnl_mMapSizes.GetButtonByName("20x20").OnClick(event)):
                InitNewMap(20, 20)
                gameMap.editMode = True
                CURRENTSTATE = EDITORSTATE

            if(pnl_mMapSizes.GetButtonByName("25x25").OnClick(event)):
                InitNewMap(25, 25)
                gameMap.editMode = True
                CURRENTSTATE = EDITORSTATE

            if(pnl_mMapSizes.GetButtonByName("15x10").OnClick(event)):
                InitNewMap(15, 10)
                gameMap.editMode = True
                CURRENTSTATE = EDITORSTATE

            if(pnl_mMapSizes.GetButtonByName("20x15").OnClick(event)):
                InitNewMap(20, 15)
                gameMap.editMode = True
                CURRENTSTATE = EDITORSTATE

            if(pnl_mMapSizes.GetButtonByName("25x20").OnClick(event)):
                InitNewMap(25, 20)
                gameMap.editMode = True
                CURRENTSTATE = EDITORSTATE

            if(pnl_mMapSizes.GetButtonByName("30x25").OnClick(event)):
                InitNewMap(30, 25)
                gameMap.editMode = True
                CURRENTSTATE = EDITORSTATE

            if(pnl_mMapSizes.GetButtonByName("Load").OnClick(event)):
                if AskMapToLoad():
                    CURRENTSTATE = EDITORSTATE

            if(pnl_mMapSizes.GetButtonByName("Continue").OnClick(event)):
                ImportMap(lastEditedMap)
                gameMap.editMode = True
                CURRENTSTATE = EDITORSTATE


        # Begin Options panel handling
        pnl_mOptions.HandleTitleButton(event)
        
        if(pnl_mOptions.GetButtonState(event, 0)):
            if gameMap.RemoveAllScores(levelPaths):
                n_Notifier.Popup("Cleared highscores")
            else:
                n_Notifier.Popup("No scores to clear")

        # Begin Credits panel handling
        # Handle credits panel inputs
        if(pnl_mCredits.GetButtonState(event, 0)):
            webbrowser.open("https://www.soundimage.org")

        elif(pnl_mCredits.GetButtonState(event, 1)):
            webbrowser.open("https://www.zapsplat.com")

        elif(pnl_mCredits.GetButtonState(event, -2)):
            pnl_mCredits.Hide()

# Handle in-game and test mode UI inputs
def HandleInGameUI(e):
    global levelTime

    if(btn_Reset.OnClick(e)):
        # print("Resetting")
        global gameMap
        pnl_Score.hide = True
        gameMap = gameMap.Reset()
        FitWindowToMap(gameMap)
        player.UpdateMap(gameMap)
        ResetLevelTimer()
        #StartLevelTimer()

    if player.stepCounter == -1:
        StopLevelTimer()
        ResetLevelTimer()

    if player.stepCounter == 0:
        StopLevelTimer()
        ResetLevelTimer()
        StartLevelTimer()
        player.stepCounter += 1

    # If the Main Menu button is pressed
    if(btn_MainMenu.OnClick(e)==True):
        global CURRENTSTATE, GAMETITLE, levelCounter

        # Ensure the score panel is hidden
        pnl_Score.hide = True

        # Check the current state to determine
        # wether or not to restart the main
        # menu music
        if CURRENTSTATE == EDITORSTATE:

            # If in the editor, don't restart music
            # as it is the same music track
            InitMainMenu(startMusic=False)

        elif CURRENTSTATE == INGAMESTATE:

            # If in-game go to main menu and
            # restart the menu music
            InitMainMenu(startMusic=True)

        # Finally set the current state to
        # to the main menu
        pygame.display.set_caption(GAMETITLE)
        CURRENTSTATE = MAINMENUSTATE

    # Handle input for the score panel
    # and update it's elements
    if(pnl_Score.GetButtonState(e) == True): # Next Level Button
        pnl_Score.GetButton().buttonIsPressed = False
        pnl_Score.hide = True
        levelCounter += 1
        isNextLevel = LoadLevel(levelCounter)

# Handle editor UI input
def HandleEditorUI(e):
    global gameMap, player, lastEditedMap, levelPaths
    if(gameMap.editMode == False):
        if(btn_Edit.OnClick(e)==True):
            ImportMap(gameMap.filePath)
            gameMap.editMode = True

    elif(gameMap.editMode == True):
        if(btn_Wall.OnClick(e) == True):
            gameMap.editSelect = 2

        if(btn_Door.OnClick(e) == True):
            gameMap.editSelect = 3

        if(btn_Key.OnClick(e) == True):
            gameMap.editSelect = 4

        if(btn_PortBegin.OnClick(e) == True):
            gameMap.editSelect = 5

        if(btn_PortEnd.OnClick(e) == True):
            gameMap.editSelect = 6

        if(btn_Player.OnClick(e) == True):
            gameMap.editSelect = 0

        if(btn_FinishPoint.OnClick(e) == True):
            gameMap.editSelect = 1

        if(btn_Save.OnClick(e)==True):
            if gameMap.filePath != '':
                gameMap.SaveMap(gameMap.filePath)
                n_Notifier.Popup("Saved: " + str(gameMap.filePath.name))
            else:
                n_Notifier.Popup("Problem Saving, map not saved.")

        if(btn_SaveNew.OnClick(e)==True):
            if gameMap.AskSaveMap():
                n_Notifier.Popup("Saved: " + str(gameMap.filePath.name))
            else:
                n_Notifier.Popup("Problem Saving, map not saved.")

        if(btn_Load.OnClick(e)==True):
            inMap = gridMap.AskLoadMap(DSURF)
            if inMap != None:
                gameMap = inMap
                UpdateEditorColors()
                gameMap.editMode = True
                FitWindowToMap(gameMap)
                player.UpdateMap(gameMap)
                pygame.display.set_caption(os.path.splitext(gameMap.filePath.name)[0])
                n_Notifier.Popup("Loading: " + str(gameMap.filePath.name))

        if(btn_RandColor.OnClick(e)):
            newColor = GetRandomColor()

            # Set Player color
            if gameMap.editSelect == 0:
                gameMap.playerColor = newColor
                btn_Player.SetFillcolor(gameMap.playerColor)

            # Set Finish color
            elif gameMap.editSelect == 1:
                gameMap.finishColor = newColor
                btn_FinishPoint.SetFillcolor(gameMap.finishColor)

            # Set Wall color
            elif gameMap.editSelect == 2:
                gameMap.wallColor = newColor
                btn_Wall.SetFillcolor(gameMap.wallColor)

            # Set Key/door color
            elif gameMap.editSelect == 3:
                gameMap.doorColors[gameMap.eCurrentDoorIndex] = newColor
                btn_Door.SetFillcolor(gameMap.doorColors[gameMap.eCurrentDoorIndex])

            elif gameMap.editSelect == 4:
                gameMap.doorColors[gameMap.eCurrentKeyIndex] = newColor
                btn_Key.SetFillcolor(gameMap.doorColors[gameMap.eCurrentDoorIndex])

            # Set portal begin and end colors
            elif gameMap.editSelect == 5:
                gameMap.portalColors[gameMap.eCurrentPortalBeginIndex] = newColor
                btn_PortBegin.SetFillcolor(gameMap.portalColors[gameMap.eCurrentPortalBeginIndex])

            elif gameMap.editSelect == 6:
                gameMap.portalColors[gameMap.eCurrentPortalEndIndex] = newColor
                btn_PortEnd.SetFillcolor(gameMap.portalColors[gameMap.eCurrentPortalEndIndex])

        if(btn_ColorPicker.OnClick(e) == True):
            root = Tk()
            color = colorchooser.askcolor()
            root.destroy()
            if not color == (None, None):
                # Set Player color
                if gameMap.editSelect == 0:
                    gameMap.playerColor = color[0]
                    btn_Player.SetFillcolor(gameMap.playerColor)

                # Set Finish color
                elif gameMap.editSelect == 1:
                    gameMap.finishColor = color[0]
                    btn_FinishPoint.SetFillcolor(gameMap.finishColor)

                # Set Wall color
                elif gameMap.editSelect == 2:
                    gameMap.wallColor = color[0]
                    btn_Wall.SetFillcolor(gameMap.wallColor)

                # Set Key/door color
                elif gameMap.editSelect == 3:
                    gameMap.doorColors[gameMap.eCurrentDoorIndex] = color[0]
                    btn_Door.SetFillcolor(gameMap.doorColors[gameMap.eCurrentDoorIndex])

                elif gameMap.editSelect == 4:
                    gameMap.doorColors[gameMap.eCurrentKeyIndex] = color[0]
                    btn_Key.SetFillcolor(gameMap.doorColors[gameMap.eCurrentDoorIndex])

                # Set portal begin and end colors
                elif gameMap.editSelect == 5:
                    gameMap.portalColors[gameMap.eCurrentPortalBeginIndex] = color[0]
                    btn_PortBegin.SetFillcolor(gameMap.portalColors[gameMap.eCurrentPortalBeginIndex])

                elif gameMap.editSelect == 6:
                    gameMap.portalColors[gameMap.eCurrentPortalEndIndex] = color[0]
                    btn_PortEnd.SetFillcolor(gameMap.portalColors[gameMap.eCurrentPortalEndIndex])

        # If the test button is clicked
        if(btn_Test.OnClick(e) == True):
            gameMap.SaveMap(gameMap.filePath)
            gameMap.editMode = False
            player.UpdateMap(gameMap)

        # If the Add to levels button is pressed
        if(btn_AddToLevels.OnClick(e)):
            print("Adding to levels folder")
            # Find an unused level number
            # and save the map with the
            # determined level name
            levelPaths = GetAllLevelPaths()
            print("Found %d existing levels"%len(levelPaths))
            unusedLevelNum = len(levelPaths) + 1
            lPath = gridMap.levelDir + "Level" + str(unusedLevelNum) + ".gmf"
            print(lPath)
            gameMap.SaveMap(lPath)
            UpdateLevelsPanel(pnl_mLevelSelect)
            n_Notifier.Popup("Saved map to Levels folder")

        # If the main menu button is pressed
        if(btn_MainMenu.OnClick(e)==True):
            global CURRENTSTATE
            if gameMap.filePath != '':
                lastEditedMap = gameMap.filePath
                gameMap.SaveMap(gameMap.filePath)

            InitMainMenu(startMusic = False)

            pygame.display.set_caption(GAMETITLE)
            CURRENTSTATE = 0

        # Handle Door Flicker
        if(fk_DoorFlicker.buttonOne.OnClick(e)):
            gameMap.eCurrentDoorIndex += 1
            print(gameMap.eCurrentDoorIndex)

        elif(fk_DoorFlicker.buttonTwo.OnClick(e)):
            gameMap.eCurrentDoorIndex -= 1
            print(gameMap.eCurrentDoorIndex)

        if(fk_KeyFlicker.buttonOne.OnClick(e)):
            gameMap.eCurrentKeyIndex += 1
            print(gameMap.eCurrentKeyIndex)

        elif(fk_KeyFlicker.buttonTwo.OnClick(e)):
            gameMap.eCurrentKeyIndex -= 1
            print(gameMap.eCurrentKeyIndex)


## Update Loops

# Update the main menu UI
def UpdateMainMenuUI():
    global DWIDTH, DHEIGHT
    txt_MainTitle.SetPos((DWIDTH/2-txt_MainTitle.GetWidth()/2, 5))

    btn_mPlay.SetPos((DWIDTH/2-btn_mPlay.width/2, 70))

    btn_mLevelSelect.SetPos((DWIDTH/2-btn_mLevelSelect.width/2, 110))

    btn_mEditMode.SetPos((DWIDTH/2-btn_mEditMode.width/2, 150))

    btn_mOptions.SetPos((DWIDTH/2-btn_mOptions.width/2, 190))

    btn_mCredits.SetPos((DWIDTH/2-btn_mCredits.width/2, 230))

    btn_mExit.SetPos((DWIDTH/2-btn_mExit.width/2, DHEIGHT-btn_mExit.height-5))

    # Increase the y position of the moving
    # decorative keys on the main menu
    menuKeys_yPositions[0] += mKeySpeed
    menuKeys_yPositions[1] += mKeySpeed
    menuKeys_yPositions[2] += mKeySpeed
    menuKeys_yPositions[3] += mKeySpeed

    # Once the moving keys go off the bottom of the screen
    # place them back at their starting position
    # to achieve an infinite scrolling effect
    if menuKeys_yPositions[0] > gameMap.mapHeight+20:
        menuKeys_yPositions[0] = -20
        menuKeyColors[0] = GetRandomColor()
        menuKeyColors[1] = GetRandomColor()

    if menuKeys_yPositions[1] > gameMap.mapHeight+20:
        menuKeys_yPositions[1] = -20
        menuKeyColors[2] = GetRandomColor()
        menuKeyColors[3] = GetRandomColor()

    if menuKeys_yPositions[2] > gameMap.mapHeight+20:
        menuKeys_yPositions[2] = -20
        menuKeyColors[4] = GetRandomColor()
        menuKeyColors[5] = GetRandomColor()

    if menuKeys_yPositions[3] > gameMap.mapHeight+20:
        menuKeys_yPositions[3] = -20
        menuKeyColors[6] = GetRandomColor()
        menuKeyColors[7] = GetRandomColor()


    pnl_mLevelSelect.Update()

    pnl_mMapSizes.Update()

    pnl_mOptions.Update()

    pnl_mCredits.Update()

    n_Notifier.Update()

    #s_VolSlider.Update()



# Update the in-game UI
def UpdateInGameUI():
    global gameMap, player
    txt_InGameTitle.SetPos((0, UIbegin_Y+10))

    txt_BestTime.SetPos((0, DHEIGHT-30))

    cBest = gameMap.currentBest
    if cBest > 0:
        txt_BestTime.SetText("Best: " + str(cBest))
    else:
        txt_BestTime.SetText("Best: n/a")

    elapsedTime = 0.0
    if pnl_Score.hide:
        if player.stepCounter >= 0:
            elapsedTime = time.time() - levelStartTime
            elapsedTime = round(elapsedTime, 2)

        txt_LevelTimer.SetText("Time: " + str(elapsedTime))
        txt_LevelTimer.SetPos((0, DHEIGHT-15))


    if CURRENTSTATE == EDITORSTATE:
        btn_Edit.SetPos((DWIDTH-btn_Test.width-2, UIbegin_Y+6))
        btn_MainMenu.SetPos((DWIDTH-btn_MainMenu.width-2, DHEIGHT-btn_MainMenu.height-1))

    elif CURRENTSTATE == INGAMESTATE:
        btn_MainMenu.SetPos((DWIDTH-btn_MainMenu.width-2, UIbegin_Y+80))
        if player.stepCounter == 0:
            StartLevelTimer()

    btn_Reset.SetPos((0, UIbegin_Y+30))

    pnl_Score.Update()
    n_Notifier.Update()

# Update editor UI element colors
def UpdateEditorColors():
    global gameMap
    btn_Player.SetFillcolor(gameMap.playerColor)
    btn_FinishPoint.SetFillcolor(gameMap.finishColor)
    btn_Wall.SetFillcolor(gameMap.wallColor)
    btn_Door.SetFillcolor(gameMap.doorColors[gameMap.eCurrentDoorIndex])
    btn_Key.SetFillcolor(gameMap.doorColors[gameMap.eCurrentKeyIndex])

    # Portal beginnings and ends indices for the editor (e)
    btn_PortBegin.SetFillcolor(gameMap.portalColors[gameMap.eCurrentPortalBeginIndex])
    btn_PortEnd.SetFillcolor(gameMap.portalColors[gameMap.eCurrentPortalEndIndex])

# Update editor UI positions
def UpdateEditorUI():
    global gameMap
    #txt_EditorTitle.SetPos((0, UIbegin_Y+10))
    btn_Wall.SetPos((100, UIbegin_Y+6))

    # Door button and it's flicker to flick
    # Through door IDs
    btnX = 175

    btn_Door.SetPos((100, UIbegin_Y+25))
    dIndex = gameMap.eCurrentDoorIndex
    btn_Door.SetText("Door: %d" % dIndex)
    doorFlickerPos = (btnX, UIbegin_Y+25)
    fk_DoorFlicker.SetPos(doorFlickerPos)

    # Same with keys
    btn_Key.SetPos((100, UIbegin_Y+44))
    kIndex = gameMap.eCurrentKeyIndex
    btn_Key.SetText("Key: %d" % kIndex)
    keyFlickerPos = ((btnX, UIbegin_Y+44))
    fk_KeyFlicker.SetPos(keyFlickerPos)

    # Portal begins
    btn_PortBegin.SetPos((100, UIbegin_Y+63))
    pbIndex = gameMap.eCurrentPortalBeginIndex
    btn_PortBegin.SetText("Portal S: %d" % pbIndex)
    PBflickerPos = ((btnX, UIbegin_Y+63))
    fk_PBeginFlicker.SetPos(PBflickerPos)

    # and portal ends
    btn_PortEnd.SetPos((100, UIbegin_Y+82))
    peIndex = gameMap.eCurrentPortalEndIndex
    btn_PortEnd.SetText("Portal E: %d" % peIndex)
    PEflickerPos = (btnX, UIbegin_Y+82)
    fk_PEndFlicker.SetPos(PEflickerPos)


    btn_ColorPicker.SetPos((0, UIbegin_Y+6))
    btn_RandColor.SetPos((0, UIbegin_Y+25))

    btn_Player.SetPos((0, UIbegin_Y+63))
    btn_FinishPoint.SetPos((0, UIbegin_Y+44))

    btn_AddToLevels.SetPos((0, UIbegin_Y+82))

    btn_Test.SetPos((DWIDTH-btn_Test.width-2, UIbegin_Y+6))
    btn_Save.SetPos((DWIDTH-btn_Save.width-2, UIbegin_Y+25))

    btn_SaveNew.SetPos((DWIDTH-btn_SaveNew.width-2, UIbegin_Y+44))
    btn_Load.SetPos((DWIDTH-btn_Load.width-2, UIbegin_Y+63))
    btn_MainMenu.SetPos((DWIDTH-btn_MainMenu.width-2, DHEIGHT-btn_MainMenu.height-1))

    UpdateEditorColors()
    n_Notifier.Update()
    fk_DoorFlicker.Update()
    fk_KeyFlicker.Update()
    fk_PBeginFlicker.Update()
    fk_PEndFlicker.Update()
## Draw Loops
def DrawMainMenuUI():
    global menuKeys_yPos, menuKeyColors, gameMap, MENUBGCOLOR
    #Begin drawing section
    DSURF.fill(MENUBGCOLOR)

    gameMap.Draw()


    # Draw Main menu border
    pygame.draw.rect(gameMap.mapSurface, BLACK, (0,0,gameMap.mapWidth,gameMap.mapHeight), 3)
    pygame.draw.line(gameMap.mapSurface, BLACK, (40, 40),(gameMap.mapWidth-40,40), 3)

    pygame.draw.rect(gameMap.mapSurface, WHITE, (75,40,gameMap.mapWidth-150,gameMap.mapHeight))
    pygame.draw.rect(gameMap.mapSurface, BLACK, (75,40,gameMap.mapWidth-150,gameMap.mapHeight), 1)

    # Draw key decorations
    gameMap.DrawKey((73, int(menuKeys_yPositions[0])), 1, menuKeyColors[0])
    gameMap.DrawKey((gameMap.mapWidth - 101, int(menuKeys_yPositions[0])), 1, menuKeyColors[1])

    # Draw more keys!
    gameMap.DrawKey((73, int(menuKeys_yPositions[1])), 1, menuKeyColors[2])
    gameMap.DrawKey((gameMap.mapWidth - 101, int(menuKeys_yPositions[1])), 1, menuKeyColors[3])


    # Draw EVEN MORE KEYS
    gameMap.DrawKey((73, int(menuKeys_yPositions[2])), 1, menuKeyColors[4])
    gameMap.DrawKey((gameMap.mapWidth - 101, int(menuKeys_yPositions[2])), 1, menuKeyColors[5])

    # WHEN IS IT GOING TO END
    # WITH THESE KEYS
    gameMap.DrawKey((73, int(menuKeys_yPositions[3])), 1, menuKeyColors[6])
    gameMap.DrawKey((gameMap.mapWidth - 101, int(menuKeys_yPositions[3])), 1, menuKeyColors[7])

    # Draw a line through all the buttons
    # on the main menu
    centerX = int(gameMap.mapWidth/2)
    pygame.draw.line(DSURF, BLACK, (centerX, 70), (centerX, 240))

    # Draw title border
    pygame.draw.rect(gameMap.mapSurface, WHITE, (40, 0, gameMap.mapWidth-80, 40))


    txt_MainTitle.Draw()
    btn_mPlay.Draw()
    btn_mLevelSelect.Draw()
    btn_mEditMode.Draw()
    btn_mOptions.Draw()
    btn_mCredits.Draw()
    btn_mExit.Draw()

    pnl_mLevelSelect.Draw()
    pnl_mMapSizes.Draw()
    pnl_mOptions.Draw()
    pnl_mCredits.Draw()

    # Draw the notifier in the top left
    # which will pop up and fade away
    # upon important actions such as
    # saving maps and clearing highscores
    n_Notifier.Draw()


    pygame.display.update()

# Draw the in-game UI elements
def DrawInGameUI():
    global gameMap, player, CURRENTSTATE
    txt_InGameTitle.Draw()

    obtainedKeyCount = 0
    xCount = 0
    yCount = 0
    xLimit = 11
    keySpacing = 18

    for k in player.keys:
        gameMap.DrawKey((50 + 18 * xCount, (UIbegin_Y+5) + (keySpacing+10) * yCount), k.isForDoor)
        obtainedKeyCount += 1
        xCount +=1
        if xCount >= xLimit:
            xCount = 0
            yCount += 1

    if CURRENTSTATE == EDITORSTATE:
        btn_Edit.Draw()
    else:
        # Only draw the level timer in game
        # not in the map editor
        txt_LevelTimer.Draw()
        txt_BestTime.Draw()

    btn_Reset.Draw()
    btn_MainMenu.Draw()
    n_Notifier.Draw()
    # If the panel is not hidden, draw it
    # score panel is only drawn at the end of each level
    pnl_Score.Draw()


def DrawEditorUI():
    #txt_EditorTitle.Draw()
    btn_Wall.Draw()
    btn_Door.Draw()
    btn_Key.Draw()
    btn_PortBegin.Draw()
    btn_PortEnd.Draw()
    btn_Player.Draw()
    btn_FinishPoint.Draw()
    btn_ColorPicker.Draw()
    btn_RandColor.Draw()
    btn_AddToLevels.Draw()

    btn_Save.Draw()
    btn_SaveNew.Draw()
    btn_Load.Draw()
    btn_Test.Draw()
    btn_MainMenu.Draw()

    blockColor = WHITE
    gameMap.DrawEditSelectThumb((55, UIbegin_Y+46))
    n_Notifier.Draw()
    fk_DoorFlicker.Draw()
    fk_KeyFlicker.Draw()
    fk_PBeginFlicker.Draw()
    fk_PEndFlicker.Draw()

## State Loops

# Main menu state loop
def MainMenuLoop():
    #global DSURF, DWIDTH, CURRENTSTATE, gameMap, EXITED, FPSCLOCK, menuKeys_yPos
    global FPSCLOCK, FPS
    HandleMainMenuUI()
    UpdateMainMenuUI()
    DrawMainMenuUI()
    FPSCLOCK.tick(FPS)

# In-game state loop
def InGameLoop():
    global player, CURRENTSTATE, gameMap, levelCounter
    global FSCLOCK, FPS, EXITED, levelTime
    keyStates = pygame.key.get_pressed()

    if player.mapCompleted == True:
        # Stop the level timer and record it's value
        lt = StopLevelTimer()
        SaveLevelTime()

        # Check if there is a next level
        nextLevelPath = CheckForLevel(levelCounter+1)

        # Update the LevelTimer text surface to represent
        # the new score
        txt_LevelTimer.SetText("Time: " + str(lt))
        sDiff = round(gameMap.currentBest-lt, 2)
        cBest = round(gameMap.currentBest, 2)

        # Check if the new score is better than the current best
        # and update the Score text surface to notify the player
        # of the results
        pnl_Score.elements[0].SetText("You finished in " + str(lt) + "sec.")

        # First clear the text for the sDiff line
        pnl_Score.elements[2].SetText("")



        if nextLevelPath == None:
            pnl_Score.GetButton().txtSurf.SetText("Fin")
        else:
            pnl_Score.GetButton().txtSurf.SetText("Next level")

        if lt > cBest:
            if cBest == 0:
                pnl_Score.elements[1].SetText("Your best is: n/a")
            else:
                pnl_Score.elements[1].SetText("Your best is: " + str(cBest) + "sec.")

        elif lt < cBest:
            pnl_Score.elements[1].SetText("Fantastic, you beat your previous highscore")
            pnl_Score.elements[2].SetText("by " + str(sDiff) + "sec!")


        player.mapCompleted = False
        pnl_Score.hide = False

    # When pnl_Score is hidden again the next level
    # is loaded elsewhere and the timer starts over
    #if pnl_Score.hide == True:
            #StartLevelTimer()

    for event in pygame.event.get():
        n_Notifier.HandleEvents(event)

        if event.type == pygame.QUIT:
            EXITED = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                InitMainMenu(startMusic=True)
                pygame.display.set_caption("Mazes")
                CURRENTSTATE = 0

            elif event.key  == pygame.K_RETURN or pygame.K_SPACE:
                if pnl_Score.hide == False:
                    print("Enter pressed")
                    #pnl_Score.Hide()
                    #pnl_Score.GetButton().buttonIsPressed = False
                    pnl_Score.hide = True
                    levelCounter += 1
                    isNextLevel = LoadLevel(levelCounter)


        HandleInGameUI(event)

        if pnl_Score.hide:
            player.HandleNormalInput(event)

    if pnl_Score.hide:
        player.HandleShiftInput(keyStates)

    UpdateInGameUI()

    #Begin drawing section
    DSURF.fill(BGCOLOR)

    gameMap.Draw()
    player.Draw()
    DrawInGameUI()
    FPSCLOCK.tick(FPS)


    pygame.display.update()

# Editor state loop
def EditorLoop():
    global player, CURRENTSTATE, gameMap, levelCounter, FSCLOCK, FPS, EXITED, dCellsize

    # Handle player motion input
    if not gameMap.editMode:
        keyStates = pygame.key.get_pressed()
        player.HandleShiftInput(keyStates)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            EXITED = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                InitMainMenu()
                pygame.display.set_caption("Mazes")
                CURRENTSTATE = MAINMENUSTATE

            elif event.key == pygame.K_1 and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                InitNewMap(10, 10)

            elif event.key == pygame.K_2 and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                InitNewMap(15, 10)

            elif event.key == pygame.K_3 and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                InitNewMap(15, 15)

            elif event.key == pygame.K_4 and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                InitNewMap(20, 15)

            elif event.key == pygame.K_5 and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                InitNewMap(20, 20)

            elif event.key == pygame.K_6 and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                InitNewMap(25, 20)

        n_Notifier.HandleEvents(event)
        player.HandleNormalInput(event)

        gameMap.HandleEditorInput(event)
        HandleEditorUI(event)

        if not gameMap.editMode:
            HandleInGameUI(event)

    # Begin drawing section
    DSURF.fill(BGCOLOR)
    gameMap.Draw()

    if not gameMap.editMode:
        if player.mapCompleted == True:
            gameMap = gridMap.LoadMap(gameMap.filePath, DSURF)
            player.UpdateMap(gameMap)
        UpdateInGameUI()
        player.Draw()
        DrawInGameUI()
        FPSCLOCK.tick(FPS)

    elif gameMap.editMode == True:
        UpdateEditorUI()
        DrawEditorUI()
        FPSCLOCK.tick(FPS)

    pygame.display.update()

# Start the menu music when the game starts
PlayMenuMusic()

## Main game loop
while not EXITED:
    if CURRENTSTATE == MAINMENUSTATE:
        MainMenuLoop()

    elif CURRENTSTATE == INGAMESTATE:
        InGameLoop()

    elif CURRENTSTATE == EDITORSTATE:
        EditorLoop()


pygame.quit()
sys.exit()
