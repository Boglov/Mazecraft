import random

# Define colors to be used when drawing
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 51)
BROWN = (79, 77, 73)
GREY = (126, 124, 114)
ORANGERED = (255, 69, 0)

# Color Palette 1
LIGHTBLUE = (196, 229, 242)
BABYBLUE = (172, 215, 237)
LAVENDAR = (216, 175, 239)

#Color Palette 2
P1C1=(23, 49, 57)
P1C2=(44, 66, 85)
P1C3=(139, 132, 105)
P1C4=(171, 197, 181)
P1C5=(28, 223, 219)

def GetRandomColor(seed = "MAZES"):
    r = random.uniform(0,255)
    g = random.uniform(0,255)
    b = random.uniform(0,255)
    newColor = (r,g,b)
    return newColor