#!/usr/bin/python3

from launchpad import *
from random import *
import time

# Drawpad
# - Can pick color using arrow keys. Pressing inner grid buttons lights up
# that pixel with that color.
# - Can change mirror modes using the "Session" button.
# - Auto mode where neat things happen. Enable using the "Drums" button.

# AutomodeBot implements the AI that works in Automode.
walkLengthMax = 50
walkLengthMin = 2
waitTimeMin = 0
waitTimeMax = 10
breakOnCollision = True
chanceOfErasure = 30
class AutomodeBot:
    def __init__(self, launchpad):
        self.walking = True
        self.walkLength = 0
        self.walkEveryXFrame = 2
        self.lp = launchpad

        self.walkSpeedWait = 0
        self.wait = 0
        self.lastx = self.lasty = 0
        self.x = self.y = 0
        self.color = 0

    def update(self):
        # If bot came to end of walk, start new one
        if (self.walkLength == 0 and self.wait <= 0):
            self.walkLength = randrange(walkLengthMin, walkLengthMax)
            self.x = randrange(0, INNER_GRID_WIDTH)
            self.y = randrange(0, INNER_GRID_HEIGHT)
            self.wait = randrange(waitTimeMin, waitTimeMax)
            if (self.color != 0 and (chanceOfErasure and randrange(0, 100) < chanceOfErasure)):
                self.color = 0
            else:
                self.color = randrange(0, 128)
            print("\nNEW X %d Y %d WAIT %d WL %d" % (self.x, self.y, self.wait, self.walkLength))

        # If bot still walking, process the walk
        elif (self.walkLength > 0):
            # Walk speed implemented via waiting x many frames before every step
            if (self.walkSpeedWait > 0):
                self.walkSpeedWait -= 1
            else:
                self.walkSpeedWait = self.walkEveryXFrame

                # Find random direction among 8 directions
                xdir = 0
                ydir = 0

                # Rule of next step coordinate:
                # wont be the last pixel we were on
                # wont be a pixel we already have been on

                # Check neighbors colors. Pick next pixel randomly out of pixels that dont have our color.
                left = (self.x-1 if self.x-1 >= 0 else (INNER_GRID_WIDTH) + (self.x-1))
                right = (self.x+1 if self.x+1 < INNER_GRID_WIDTH else (self.x+1) - INNER_GRID_WIDTH)
                down = (self.y-1 if self.y-1 >= 0 else (INNER_GRID_HEIGHT) + (self.y-1))
                up = (self.y+1 if self.y+1 < INNER_GRID_HEIGHT else (self.y+1) - INNER_GRID_HEIGHT)
                neighborCoords = [(left, down),
                                  (left, self.y),
                                  (left, up),
                                  (self.x, up),
                                  (self.x, down),
                                  (right, down),
                                  (right, self.y),
                                  (right, up)]

                neighborColors = [self.lp.GetPixel(x, y).GetColor() for (x, y) in neighborCoords]
                if (breakOnCollision):
                    possibleCoords = [(x, y) for (x, y) in neighborCoords if (self.lp.GetPixel(x, y).GetColor() != self.color)]
                else:
                    possibleCoords = neighborCoords

                if (len(possibleCoords)):
                    (self.x, self.y) = possibleCoords[randrange(0, len(possibleCoords))]
                    self.walkLength -= 1
                else:
                    self.walkLength = 0

        # If bot done walking, is waiting
        elif (self.wait > 0):
            self.wait -= 1

        print("x:%d->%d y:%d->%d w:%d l:%d c:%d" % (self.lastx, self.x, self.lasty, self.y, self.wait, self.walkLength, self.color))
        self.lastx = self.x
        self.lasty = self.y
        return (self.x, self.y, self.color)

lp = LaunchpadMiniMk3()
a = AutomodeBot(lp)

automodeEnabled = False

color = 0

# Mirror Modes
# 0 : DISABLED
# 1 : HORIZONTAL
# 2 : VERTICAL
# 3 : 4WAY
mirrormodes = 0

def buttonRelease(msg):
    print("BUTTON RELEASE", msg)

def controlChange(msg):
    global color, mirrormodes, automodeEnabled
    print("CONTROL CHANGE", msg)
    button = msg.control
    if (msg.value == 0): # RELEASE
        pass
    elif (msg.value == 127): # PRESS
        if (button == CB_UPARROW): # CHANGE COLOR
            color += 1
        if (button == CB_DOWNARROW): # CHANGE COLOR
            color -= 1
        if (button == CB_RIGHTARROW):
            pass
        if (button == CB_LEFTARROW):
            pass
        if (button == CB_SESSION): # 4WAY MIRROR
            mirrormodes += 1
            mirrormodes = mirrormodes % 4
            lp.SetPixel(4, 8, (mirrormodes * 20))
        if (button == CB_DRUMS):
            automodeEnabled = ~(automodeEnabled)
            lp.SetPixel(5, 8, (20 if automodeEnabled else 0))
        if (button == CB_KEYS):
            pass
        if (button == CB_USER): # CLEAR GRID
            for x in range(0, INNER_GRID_WIDTH):
                for y in range(0, INNER_GRID_HEIGHT):
                    lp.SetPixel(x, y, 0)

        if (color < 0):
            color = color + 128
        color = color % 128
        updateColorSignifier()

def buttonPress(msg):
    x = (msg.note % 10) - 1
    y = int(msg.note / 10) - 1
    lp.SetPixel(x, y, color)
    if (mirrormodes == 1): # HORIZONTAL MIRROR
        x1 = x
        y1 = INNER_GRID_HEIGHT - y - 1
        lp.SetPixel(x1, y1, color)
    if (mirrormodes == 2): # VERTICAL MIRROR
        x1 = INNER_GRID_WIDTH - x - 1
        y1 = y
        lp.SetPixel(x1, y1, color)
    if (mirrormodes == 3): # FOUR WAY MIRROR
        x1 = INNER_GRID_WIDTH - x - 1
        y1 = y
        x2 = x
        y2 = INNER_GRID_HEIGHT - y - 1
        x3 = INNER_GRID_WIDTH - x - 1
        y3 = INNER_GRID_HEIGHT - y - 1
        lp.SetPixel(x1, y1, color)
        lp.SetPixel(x2, y2, color)
        lp.SetPixel(x3, y3, color)
    print("BUTTON PRESS x %d, y %d" % (x, y))

def autoButtonPress(x, y, c): # TODO make this better. could codeshare
    lp.SetPixel(x, y, c)
    if (mirrormodes == 1): # HORIZONTAL MIRROR
        x1 = x
        y1 = INNER_GRID_HEIGHT - y - 1
        lp.SetPixel(x1, y1, c)
    if (mirrormodes == 2): # VERTICAL MIRROR
        x1 = INNER_GRID_WIDTH - x - 1
        y1 = y
        lp.SetPixel(x1, y1, c)
    if (mirrormodes == 3): # FOUR WAY MIRROR
        x1 = INNER_GRID_WIDTH - x - 1
        y1 = y
        x2 = x
        y2 = INNER_GRID_HEIGHT - y - 1
        x3 = INNER_GRID_WIDTH - x - 1
        y3 = INNER_GRID_HEIGHT - y - 1
        lp.SetPixel(x1, y1, c)
        lp.SetPixel(x2, y2, c)
        lp.SetPixel(x3, y3, c)
    print("BUTTON PRESS x %d, y %d" % (x, y))


def updateColorSignifier():
    lp.SetPixel(8, 8, color)

def main():
    # Register launchpad callbacks
    lp.onButtonPressCb = buttonPress
    lp.onButtonReleaseCb = buttonRelease
    lp.onControlChangeCb = controlChange
    lp.ClearGrid()
    updateColorSignifier()
    lp.SelectLayout(LAYOUT_PROGRAMMER)
    running = True
    while(running):
        try:
            if (automodeEnabled):
                x, y, c = a.update()
                autoButtonPress(x, y, c)
            lp.Poll()
            time.sleep(0.01)
        except KeyboardInterrupt:
            running = False
    lp.SelectLayout(LAYOUT_CUSTOM1)

if __name__ == "__main__":
    main()
