import pygame
import os
from gxColors import *

pygame.init()
pygame.font.init()
homeDir = os.path.dirname(os.path.realpath(__file__))

defaultFontSize = 15
defaultFont = pygame.font.SysFont('Times New Roman', defaultFontSize)

# Timer event for popup notes
popupTimerEvent = pygame.USEREVENT + 1

# Define values for UI elements on a panel
UIBUTTON = 0
UITEXT = 1
UIFLICKER = 2
UISLIDER = 3

def isWithinRect(point, rect):
    if point[0] >= rect[0] and point[0] <= rect[0] + rect[2]:
        if point[1] >= rect[1] and point[1] <= rect[1] + rect[3]:
            return True
    else:
        return False

def clip(val, min, max):
    if val < min:
        val = min
    elif val > max:
        val = max
    return val


#Class to manage game text easily
class GX_Text:
    def __init__(self, gameSurf, txt, tColor, p=(0,0), fSize = defaultFontSize):
        self.textStr=str(txt)
        self.pos=(p[0],p[1])
        self.color = tColor
        self.font = pygame.font.SysFont('Times New Roman', fSize)
        self.destSurf = gameSurf
        self.text=self.font.render(self.textStr, True, self.color)

    def SetColor(self, c):
        self.color = c
        self.txtSurf = GX_Text(self.destSurf, self.text, self.color, (self.pos[0], self.pos[1]))

    def SetText(self, txt):
        self.textStr=str(txt)
        self.text=self.font.render(self.textStr, True, self.color)

    def SetPos(self, p):
        self.pos = p

    def GetWidth(self):
        #tWidth = len(self.textStr) * (defaultFontSize/1.8)
        tWidth = self.font.size(self.textStr)[0]
        return tWidth

    def Update(self):
        self.text=self.font.render(self.textStr, True, self.color)

    def Draw(self):
        self.destSurf.blit(self.text, (self.pos))

class GX_Note:
    defaultTextColor = GREEN
    def __init__(self, gameSurf, p=(0,0), textStr=''):
        self.pos = p
        self.textColor = self.defaultTextColor
        self.textString = textStr

        self.destSurf = gameSurf
        self.textSurf = GX_Text(gameSurf, textStr, self.textColor, (p[0]+2, p[1]))

        self.padSize = 2
        self.width = self.textSurf.GetWidth()+self.padSize*2
        self.height = 20

        self.rect = (self.pos[0], self.pos[1], self.width, self.height)
        self.borderSize = 1
        self.borderColor = BLACK
        self.fillColor = WHITE

        self.isShowing = False
        self.fadeTime = 2 # Seconds

        self.lengthLimit = 20 # Characters

    def SetPos(self, p):
        self.pos = p
        self.rect = (self.pos[0], self.pos[1], self.width, self.height)
        self.textSurf.SetPos((p[0]+2, p[1]))

    def SetText(self, newTextStr, newColor = defaultTextColor):
        self.textString = newTextStr
        self.textSurf.SetColor(newColor)
        self.textSurf.SetText(self.textString)
        self.width = self.textSurf.GetWidth()+self.padSize*2
        self.rect = (self.pos[0], self.pos[1], self.width, self.height)

    def SetFadeTime(self, newFadeTime):
        self.fadeTime = newFadeTme

    def Popup(self, newText = '', p=None):
        if newText != '':
            self.SetText(newText)

        if p != None:
            self.SetPos(p)

        self.isShowing = True
        fadeTimeInMs = self.fadeTime * 1000
        pygame.time.set_timer(popupTimerEvent, fadeTimeInMs)
        print("Note Popped up")

    def SetTextColor(self, newColor):
        self.textSurf.SetColor(newColor)

    def HandleEvents(self, event):
        if event.type == popupTimerEvent:
            self.isShowing = False
            pygame.time.set_timer(popupTimerEvent, 0)
            print("Note faded")

    def Update(self):
        if self.isShowing:
            self.rect = (self.pos[0], self.pos[1], self.width, self.height)

    def Draw(self):
        if self.isShowing:
            pygame.draw.rect(self.destSurf, self.fillColor, self.rect)
            pygame.draw.rect(self.destSurf, self.borderColor, self.rect, self.borderSize)

            self.textSurf.Draw()

class GX_Button:
    buttonIsPressed = False
    def __init__(self, gameSurf, bText, bPos = (0,0)):
        self.pos = (bPos[0], bPos[1])
        self.width = defaultFont.size(bText)[0] + 5
        self.height = defaultFontSize+2
        self.text = bText
        self.textColor = WHITE
        self.borderColor = BLACK
        self.highlightColor = GREY
        self.fillColor = GREY
        self.destSurf = gameSurf
        self.rect = (self.pos[0], self.pos[1], self.width, self.height)
        self.txtSurf = GX_Text(gameSurf, self.text, self.textColor,\
                              (self.pos[0]+(self.width/2)-defaultFont.size(self.text)[0]/2, self.pos[1]))
        self.isClicked = False

    def SetText(self, newTextStr):
        self.text = newTextStr
        self.txtSurf = GX_Text(self.destSurf, self.text, self.textColor,\
                              (self.pos[0]+(self.width/2)-defaultFont.size(self.text)[0]/2, self.pos[1]))
        self.width = defaultFont.size(newTextStr)[0] + 5
        self.height = defaultFontSize+2

    def GetWidth(self):
        return self.width

    def OnClick(self, e):
        # Reset the butons isClicked value at the
        # beginning of each frame
        self.isClicked = False
        # Checks the event que to see if
        # the left mouse button is clicked
        # and if the mouse is within the button rect
        # if so set isClicked to True and return its value
        if e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:
                if not self.buttonIsPressed:
                    # Ensure no more than one button can
                    # be pressed at any given time
                    self.buttonIsPressed = True
                    mousePos = pygame.mouse.get_pos()
                    if isWithinRect(mousePos, (self.pos[0], self.pos[1], self.width, self.height)):
                        #print(self.text, " Selected")
                        self.isClicked = True
                        #print("isClicked:", self.isClicked)
                        #print(self.text, " Selected")

        elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1:
                    if self.buttonIsPressed == True:
                        self.buttonIsPressed = False

                    if self.isClicked == True:
                        self.isClicked = False

        return self.isClicked

    def SetFillcolor(self, c):
        self.fillColor = c
        sumVal = (c[0]+c[1]+c[2])
        if (sumVal < 255):
            self.textColor = WHITE
        else:
            self.textColor = BLACK

        self.txtSurf = GX_Text(self.destSurf, self.text, self.textColor,\
                              (self.pos[0]+(self.width/2)-defaultFont.size(self.text)[0]/2, self.pos[1]))

    def SetPos(self, p):
        self.pos = p
        self.txtSurf.SetPos((self.pos[0]+(self.width/2)-defaultFont.size(self.text)[0]/2+1, self.pos[1]))
        self.rect = (self.pos[0], self.pos[1], self.width,self.height)

    def Update(self):
        self.txtSurf.Update()

    def Draw(self):
        pygame.draw.rect(self.destSurf, self.fillColor, (self.pos[0], self.pos[1], self.width, self.height))
        pygame.draw.rect(self.destSurf, self.borderColor, (self.pos[0], self.pos[1], self.width, self.height), 2)

        mousePos = pygame.mouse.get_pos()

        if isWithinRect(mousePos, self.rect):
            if self.isClicked:
                pygame.draw.rect(self.destSurf, GREEN, (self.pos[0], self.pos[1], self.width, self.height), 2)
            else:
                pygame.draw.rect(self.destSurf, self.fillColor, (self.pos[0], self.pos[1], self.width, self.height), 2)


        self.txtSurf.Draw()

class GX_CheckBox:
    boxIsClicked = False
    def __init__(self, gameSurf, p=(0,0)):
        self.destSurf = gameSurf
        self.pos = p
        self.rect = pygame.Rect((p[0], p[1]), (10, 10))
        self.borderSize = 1
        self.borderColor = BLACK
        self.highlightColor = WHITE
        self.fillColor = WHITE
        self.checkColor = BLACK
        self.mouseHovering = False
        self.isClicked = False
        self.isChecked = False

    def GetCheckState(self):
        return self.isChecked

    def Handle(self, event):
        mousePos = pygame.mouse.get_pos()
        self.mouseHovering = False
        self.isClicked = False

        if isWithinRect(mousePos, self.rect):
            self.mouseHovering = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.isClicked = True
                    self.isChecked = not self.isChecked

    def Update(self):
        no = True

    def Draw(self):
        if self.isChecked:
            pygame.draw.rect(self.destSurf, self.checkColor, self.rect)
        else:
            pygame.draw.rect(self.destSurf, self.fillColor, self.rect)


        if self.mouseHovering:
            pygame.draw.rect(self.destSurf, self.highlightColor, self.rect, self.borderSize)

        else:
            pygame.draw.rect(self.destSurf, self.borderColor, self.rect, self.borderSize)





class GX_Slider:
    def __init__(self, gameSurf, p=(0,0)):
        self.destsurf = gameSurf
        self.minVal = 0
        self.maxVal = 100

        self.valRange = self.maxVal - self.minVal
        self.currentVal = self.maxVal

        self.pos = p

        self.width = 80
        self.height = 20
        self.sliderX = self.width
        self.stepSize = int(self.width/self.valRange)
        self.capDim = (5, self.height)
        self.valueSurf = GX_Text(gameSurf, str(self.maxVal), BLACK, (p[0], p[1]-30))
        halfHeight = int(self.height/2)
        self.sliderButton = GX_Button(gameSurf, "  ", ( self.pos[0], self.pos[1]-halfHeight+3))
        self.sliderButton.SetFillcolor(WHITE)
        self.sliderWidth = self.sliderButton.GetWidth()
        self.isSliding = False


    def SetPos(self, p):
        self.pos = p
        halfHeight = int(self.height/2)
        sX = self.pos[0]+self.sliderX
        self.sliderButton.SetPos((sX, self.pos[1]-halfHeight+3))
        w = self.width
        vSurf = self.valueSurf
        self.valueSurf.SetPos((p[0] + int(w/2) - int(vSurf.GetWidth()/2) , p[1]-22))


    def GetWidth(self):
        return self.width

    def HandleSlider(self, event):
        if self.sliderButton.OnClick(event):
            self.isSliding = True
            print("Sliding: %d" % self.isSliding)

        sW = self.sliderWidth
        halfHeight = int(self.height/2)
        sRailRect = ((self.pos[0], self.pos[1], self.width + sW, halfHeight/2))
        mousePos = pygame.mouse.get_pos()
        sliderCenter = sW/2
        capSize = self.capDim
        w = self.width
        h = self.height
        halfHeight = int(h/2)
        rVal = self.GetValue()

        # Allow adjustment of current value by clicking within the
        # sliders rail rect
        if event.type == pygame.MOUSEBUTTONDOWN:
            if isWithinRect(mousePos, sRailRect) and self.isSliding is False:

                self.sliderX = mousePos[0] - self.pos[0]
                clX = clip(self.sliderX, self.pos[0], self.pos[0] + w - capSize[0] - sW)
                self.sliderButton.SetPos((int(clX), self.pos[1]-halfHeight+3))

                rVal = self.GetValue()
                self.isSliding = True

                #print("Hovering is creepy")


        if self.isSliding:
            mousePos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.isSliding = False

            clippedX = clip(mousePos[0]-sliderCenter, self.pos[0], self.pos[0] + w)

            self.sliderX = clippedX - self.pos[0]
            self.sliderButton.SetPos((int(clippedX), self.pos[1]-halfHeight+3))
            rVal = self.GetValue()
            #print(self.sliderX)
            return rVal

    def SetValue(self, newVal):
        self.currentVal = newVal
        self.valRange = self.maxVal - self.minVal
        vRange = self.valRange
        w = self.width
        h = self.height
        halfHeight = int(h/2)
        newX = self.pos[0] + (newVal/vRange)*w
        self.sliderX = newX - self.pos[0]
        self.sliderButton.SetPos((int(self.sliderX), self.pos[1]-halfHeight+3))

        return self.GetValue()

    def GetValue(self):
        # Determine the value of the slider by solving what
        # amount of pixels(stepSize) constitute one value
        # within the range of minVal and maxVal

        self.sliderWidth = self.sliderButton.GetWidth()
        self.valRange = self.maxVal - self.minVal
        vRange = self.valRange
        #totalPixels = self.width - self.capDim[0]*2 - self.sliderWidth


        w = self.width
        h = self.height
        #self.stepSize = vRange/w
        relSliderX = self.sliderX

        self.currentVal = self.minVal + (relSliderX/w)*vRange

        cValRounded = round(self.currentVal, 1)
        self.valueSurf.SetText(cValRounded)

        return self.currentVal

    def Update(self):
        self.valueSurf.SetPos((self.pos[0]-5, self.pos[1]-30))
        self.valRange = self.maxVal - self.minVal
        self.sliderWidth = self.sliderButton.GetWidth()
        #self.stepSize = int(self.width/self.valRange)

    def Draw(self):
        halfHeight = int(self.height/2)
        qHeight = int(halfHeight/2)
        w = self.width
        h = self.height
        capSize = self.capDim
        self.sliderWidth = self.sliderButton.GetWidth()
        sW = self.sliderWidth

        # Draw the left cap
        pygame.draw.rect(self.destsurf, BLACK, (self.pos[0]-capSize[0], self.pos[1]-halfHeight+2, capSize[0], h))

        # Draw the right cap
        pygame.draw.rect(self.destsurf, BLACK, (self.pos[0]+ w + sW, self.pos[1]-halfHeight+2, capSize[0],h))

        # Draw the slider rail
        mousePos = pygame.mouse.get_pos()
        sRailRect = ((self.pos[0], self.pos[1], self.width + sW, halfHeight/2))


        if isWithinRect(mousePos, sRailRect) and self.isSliding is False:
            pygame.draw.rect(self.destsurf, WHITE, sRailRect, 1)


        else:
            pygame.draw.rect(self.destsurf, BLACK, sRailRect, 1)

        self.sliderButton.Draw()
        self.valueSurf.Draw()

class GX_Flicker:
    def __init__(self, gameSurf, p=(0,0)):
        self.destSurf = gameSurf
        self.pos = p
        self.buttonOne = GX_Button(gameSurf, "/\\")
        self.buttonTwo = GX_Button(gameSurf, "\/")

    def SetPos(self, p):
        self.pos = p
        btn1Pos = p
        btn2Pos = (p[0] + 15, p[1])
        self.buttonOne.SetPos(btn1Pos)
        self.buttonTwo.SetPos(btn2Pos)

    def Update(self):
        self.buttonOne.Update()
        self.buttonTwo.Update()

    def Draw(self):
        self.buttonOne.Draw()
        self.buttonTwo.Draw()



class GX_Panel:
    def __init__(self, gameSurf, pos, pTitle = "Complete", hide = True):

        # The display surface to which the
        # panel and it's elements are drawn
        self.destSurf = gameSurf

        # The rect which defines the position and
        # size of the actual panel
        self.panelRect = (pos[0], pos[1],1,1)

        # The indicator for wether or not to
        # draw, update, or handle inputs
        # for the panel and its elements
        self.hide = hide

        # The background color of the panel
        self.fillColor = GREY

        # The color of the actual panel border
        self.borderColor = BLACK

        # The size of the actual panel border
        self.borderSize = 2

        # The height of the "handle bar" piece
        # of the panel
        self.handleSize = 18


        ## Panel Element data
        # Stores all panel elements in one list
        # for easier iteration
        self.elements = []

        # The list of colors to be used for drawing
        # certain elements
        self.elementColors = [BLACK]

        # The base size to allocate for each added
        # element
        self.elementSize = 20

        # The total amount of elements which have been
        # aded to the panel
        self.elementCount = 0

        # The amount of pixels between each element
        # and between the panel border
        self.elementSpacing = 6

        ## Panel button data
        # Stores UI buttons to their own list for
        # easier input handling
        self.buttons = []

        # Keeps track of the amount of buttons
        # the panel has for easier indexing
        self.buttonCount = 0

        ## Panel text data
        # Stores UI text elements to their own list
        # for easier input handling
        self.texts = []

        # Keeps track of the amount of text elements
        # the panel has for easier indexing
        self.textCount = 0

        self.sliders = []
        self.sliderCount = 0
        # This may possibly be used later to
        # allow panels to prevent other inputs
        # when they are being shown
        self.pauseWhenShown = True

        # The panels title text string
        self.titleStr = pTitle

        # The panels title text surface
        self.title = GX_Text(gameSurf, pTitle, BLACK)

        # The color of the panels handle bar
        self.titleColor = WHITE

        # Store the size of the given display
        # surface for use in placement of elements
        self.windowSize = gameSurf.get_size()

        # Specifies wether or not the panel is
        # centered within the windowSize
        self.centered = True

        # Center the panel horizontally
        self.hCentered = False

        # Specifies wether or not to center
        # the elements within the panel
        self.centeredElements = True

        # The maximum number of elements
        # in a column before going on to
        # a new column
        self.rowLimit = 7

        # The current index of elements in
        # each column as they are iterated
        self.rowCounter = 0
        self.colWidth = 70

        # Determines wether or not this panel
        # has a back button
        self.hasBackButton = False

        # The actual back button element
        self.backButton = GX_Button(self.destSurf, "Back", (0,0))

        # Allows for a button to replace the title text
        self.titleIsButton = False

        # The actual title button element
        self.titleButton = GX_Button(self.destSurf, self.titleStr)

        self.titleButton.SetFillcolor(WHITE)

    def Toggle(self):
        self.hide = not self.hide

    def Hide(self):
        self.hide = True

    def UnHide(self):
        self.hide = False

    def AddBlank(self):
        self.AddElement(UITEXT, isBlank = True)

    def AddElement(self, eType, eStr = "", rPos = (-1, -1), isBlank = False):

        # Add the element to the panels jumble list of
        # elements, and add specific UI elements to
        # their respective lists

        # Note: Element positions are relative to
        # that of the parenting panel (hence rPos)

        # Note: If the elements positions are set
        # manually, the dimensions of the panel
        # must be set manualy as well. As the
        # panel doesn't automaticaly expand when
        # doing so.

        # If the elements relative position is specified
        # on initialization, set it's relative
        # position to that >
        relativePos = rPos
        pRect = self.panelRect
        if rPos != (-1, -1):

            relativePos = (self.panelRect[0] + rPos[0], self.panelRect[1] + rPos[1])

            if eType == UIBUTTON:
                # Create a new button using specified
                # relative position
                newButton = GX_Button(self.destSurf, eStr, relativePos)

                # Append it to this panels elements list
                self.elements.append(newButton)

                # As well as to the buttons list
                self.buttons.append(newButton)

                #Increment the button count
                self.buttonCount += 1

            elif eType == UITEXT:

                newText = GX_Text(self.destSurf, eStr, self.elementColors[0], relativePos)
                self.elements.append(newText)
                if not isBlank:
                    self.texts.append(newText)
                    self.textCount += 1

        # Otherwise if the elements relative position is not specified
        # on initialization, automatically add it to the
        # end of the panel, in result expanding the
        # panels height to account for the new element >
        else:
            tsize = self.handleSize

            if not self.centeredElements:
                #print("Count:", self.rowCounter)
                #print("Limit:", self.rowLimit)

                relativePos = (pRect[0] + (100 * self.rowCounter), pRect[1] + tsize + self.elementCount * self.elementSize)

            elif self.centeredElements == True:
                # If the elements are to be centered
                # center them
                pWidth = self.panelRect[2]
                pCenterX = int(self.panelRect[0] + pWidth/2)

                relativePos = (self.panelRect[0] + pCenterX, self.panelRect[1] + tsize + self.elementCount * self.elementSize)

            if eType == UIBUTTON:
                # Create a new button using specified
                # relative position
                newButton = GX_Button(self.destSurf, eStr, relativePos)

                # Append it to this panels elements list
                self.elements.append(newButton)

                # As well as to the buttons list
                self.buttons.append(newButton)

                #Increment the button count
                self.buttonCount += 1

            elif eType == UITEXT:
                newText = GX_Text(self.destSurf, eStr, self.elementColors[0], relativePos)
                self.elements.append(newText)
                if not isBlank:
                    self.texts.append(newText)
                    self.textCount += 1

            elif eType == UISLIDER:
                newSlider = GX_Slider(self.destSurf, relativePos)
                newSlider.sliderButton.SetText(eStr)
                self.elements.append(newSlider)
                self.sliders.append(newSlider)
                self.sliderCount += 1

            self.rowCounter += 1
            if self.rowCounter >= self.rowLimit:
                self.rowCounter = 0

        self.elementCount += 1

    def PopElement(self, eID):
        if eID == -1:
            thisElementID = self.elementCount-1
            thisElement = self.elements[thisElementID]


            if isinstance(thisElement, GX_Button):
                thisButtonID  = self.buttonCount-1
                self.buttons.pop(thisButtonID)
                self.buttonCount -= 1

            elif isinstance(thisElement, GX_Text):
                thisTextID = self.textCount-1
                self.texts.pop(thisTextID)
                self.textCount -= 1

            elif isinstance(thisElement, GX_Slider):
                thisSliderID = self.sliderCount-1
                self.sliders.pop(thisSliderID)
                self.sliderCount -= 1

            self.elements.pop(thisElementID)
            self.elementCount -= 1


    def GetButtonState(self, event, buttonID = 0):
        checkResult = False
        # While the panel is not hidden
        if self.hide == False:

            # Check that the given buttonID is within the range
            # of the panels button count, return wether
            # or not that buton has been clicked
            if buttonID < self.buttonCount and buttonID >= 0:
                if self.buttons[buttonID].OnClick(event):
                    checkResult = True

            # If -1 is entered, return the state of the title
            # button if titleIsButton is True
            elif buttonID == -1:
                if self.titleIsButton:
                    if self.titleButton.OnClick(event):
                        checkResult = True

            # If -2 is entered as the buttonID and hasBackButton
            # is true, return its state
            elif buttonID == -2:
                if self.hasBackButton:
                    if self.backButton.OnClick(event):
                        checkResult = True

        # If the panel is hidden
        # just return False
        return checkResult

    def GetButton(self, buttonID = 0):
        # Returns the desired button using
        # only its index in the buttons list
        # so long as buttonID is within the
        # range of buttonCount
        if buttonID < self.buttonCount and buttonID >= 0:
            desiredButton = self.buttons[buttonID]
            return desiredButton

    def GetButtonByName(self, bName):
        btnCounter = 0
        theButton = None

        for btn in self.buttons:
            if btn.text == bName:
                theButton = self.buttons[btnCounter]
            btnCounter += 1

        return theButton

    def HandleTitleButton(self, event):
        if self.titleIsButton:
            if(self.GetButtonState(event, -1)):
                self.Toggle()

    def GetTextItem(self, textID = 0):
        if textID < self.textCount and textID >= 0:
            desiredText = self.texts[textID]
            return desiredText
        else:
            return None

    def GetSlider(self, sID):
        reqSlider = self.sliders[sID]
        return reqSlider

    def GetSliderVal(self, event, sID):
        if sID < self.sliderCount and sID >= 0:
            return self.sliders[sID].HandleSlider(event)

        return None

    def SetTextColor(self, textID, newColor):
        if textID < self.textCount and textID >= 0:
            self.texts[textID].SetColor(newColor)
            return True
        else:
            return False

    def UpdateSurface(self, sizeRect = (0,0,0,0)):
        # Update the reference to the
        # size of the new display surface
        # used to correctly place the panel
        # if it is set to be centered
        self.windowSize = self.destSurf.get_size()
        self.Update()

        #print(self.windowSize)

    def Update(self):
        if not self.IsHiding():
            eSpacing = self.elementSpacing
            eSize = self.elementSize
            eCount = self.elementCount
            hSize = self.handleSize

            rCounter = 0
            cCounter = 0
            pRect = self.panelRect
            newPos = (pRect[0], pRect[1])
            # If the panel is set to be centered
            # set it's position to the center of
            # the display surface
            if self.centered:

                # First ensure centered and hCentered won't
                # ever be True at the same time
                self.hCentered = False


                # Get the center point of the display surface
                centerX = int(self.windowSize[0]/2)
                centerY = int(self.windowSize[1]/2)

                # Get the half width and height of the panel
                halfWidth = int(self.panelRect[2]/2)
                halfHeight = int(self.panelRect[3]/2)

                # Set the new position to the center point of
                # the display surface, subtracting half the
                # width and height of the panel to perfectly
                # center it within the window
                newPos = (centerX-halfWidth-1, centerY-halfWidth)


            # Determine the height of the panel
            # automaticaly based on the total
            # element count multiplied by the
            # base element size and offset on
            # the y axis by the size of the handle
            # and spacing value

            elif self.hCentered:
                self.centered = False

                # Get the center point of the display surface
                centerX = int(self.windowSize[0]/2)
                halfWidth = int(self.panelRect[2]/2)
                newPos = ((centerX - halfWidth), self.panelRect[1])

            if self.centeredElements:
                if self.hasBackButton:
                    newHeight = ((self.elementCount+1)*eSize) + hSize + eSpacing*2
                else:
                    newHeight = ((self.elementCount)*eSize) + hSize + eSpacing*2
            else:
                if self.hasBackButton:
                    newHeight = ((self.rowLimit+2)*eSize) + hSize + eSpacing*2
                else:
                    newHeight = (self.rowLimit*eSize) + hSize + eSpacing*2

            # The temporary rect used to define and update
            # the position and size of the actual panel rect
            updatedRect = (newPos[0], newPos[1], 290, newHeight)

            # Set the panels actual rect to the updated one
            self.panelRect = updatedRect
            pRect = self.panelRect

            # Get the center point of the panel
            pWidth = self.panelRect[2]
            pCenterX = int(pWidth/2)

            # Place the title surface within the panel handle
            # which is centered by default
            tWidth = self.title.GetWidth()
            if self.titleIsButton:
                self.titleButton.SetPos((pRect[0]+3+pCenterX - tWidth/2- 2, pRect[1]))
            else:
                self.title.SetPos((pRect[0]+3+pCenterX - tWidth/2- 2, pRect[1]))

            # Track the current element index to correctly
            # position each element
            itmCount = 0

            # Loop through all the elements and update their
            # positions relative to the panel

            for item in self.elements:
                item.Update()
                # Determine the y offset of each element
                # based on its index and the base element
                # size value
                yOffset = hSize + eSpacing + (itmCount * eSize)
                itmWidth = item.GetWidth()

                if self.centeredElements:

                    # If elements are set to be centered
                    # set their position to the horizontal
                    # center of the panel
                    xOffset = pCenterX - itmWidth/2 - eSpacing
                    item.SetPos((pRect[0]+eSpacing + xOffset, pRect[1] + yOffset))

                else:
                    # Otherwise set their positions to be
                    # left aligned, continuing on to the
                    # next column once reaching the given
                    # rowLimit
                    xOffset = eSpacing+(cCounter*self.colWidth)
                    yOffset = hSize + eSpacing + (rCounter * eSize)
                    item.SetPos((pRect[0] + xOffset, pRect[1] + yOffset))

                itmCount+=1

                rCounter += 1
                if(rCounter >= self.rowLimit):
                    cCounter += 1
                    rCounter = 0
            # Finally, update the back button if
            # hasBackButton is true
            if self.hasBackButton:
                self.backButton.Update()
                if self.centeredElements:
                    yOffset = hSize + eSpacing + self.elementCount*eSize
                else:
                    yOffset = hSize + eSpacing + ((self.rowLimit+1) * eSize)-6

                self.backButton.SetPos((pRect[0] + eSpacing, pRect[1] + yOffset))


    def IsHiding(self):
        isHiding = self.hide
        return isHiding

    def Draw(self):
        if not self.IsHiding():
            # Fill the panel with given fillcolor
            pygame.draw.rect(self.destSurf, self.fillColor, self.panelRect)

            # Draw a border around the panel
            pygame.draw.rect(self.destSurf, self.borderColor, self.panelRect, self.borderSize)

            # Fill the title bar with the given title color
            pygame.draw.rect(self.destSurf, self.titleColor, (self.panelRect[0], self.panelRect[1], self.panelRect[2],
                             self.handleSize))

            # Draw the handle bar border with the given border color
            pygame.draw.rect(self.destSurf, self.borderColor, (self.panelRect[0], self.panelRect[1], self.panelRect[2],
                             self.handleSize), self.borderSize)

            # Draw the title surface in the handle part
            # of the panel
            if self.titleIsButton:
                self.titleButton.Draw()
            else:
                self.title.Draw()

            for item in self.elements:
                item.Draw()

            if self.hasBackButton:
                self.backButton.Draw()
