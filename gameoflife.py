#!/usr/bin/python3

from launchpad import *
from random import *
from common import *
import time

# Game of Life
'''
Any live cell with fewer than two live neighbours dies.
Any live cell with two or three live neighbours lives on.
Any live cell with more than three live neighbours dies.
Any dead cell with exactly three live neighbours becomes a live cell.
'''

class GoLBoard:
    def __init__(self, launchpad):
        self.launchpad = launchpad
        self.currentFrame = [[0 for x in range(INNER_GRID_WIDTH)] for y in range(INNER_GRID_HEIGHT)]
        self.nextFrame = [[0 for x in range(INNER_GRID_WIDTH)] for y in range(INNER_GRID_HEIGHT)]

    def reset(self):
        self.currentFrame = [[0 for x in range(INNER_GRID_WIDTH)] for y in range(INNER_GRID_HEIGHT)]
        self.nextFrame = [[0 for x in range(INNER_GRID_WIDTH)] for y in range(INNER_GRID_HEIGHT)]

    def setCell(self, x, y):
        global color
        self.currentFrame[y][x] = color

    def drawFrame(self):
        for y in range(0, INNER_GRID_HEIGHT):
            for x in range(0, INNER_GRID_WIDTH):
                self.launchpad.SetPixel(x, y, self.currentFrame[y][x])

    def printFrame(self):
        for y in range(0, INNER_GRID_HEIGHT):
            print(self.currentFrame[INNER_GRID_HEIGHT - y - 1])

    def play(self):
        global color
        for y in range(0, len(self.currentFrame)):
            for x in range(0, len(self.currentFrame[y])):
                neighbors = []
                currentValue = self.currentFrame[y][x]
                for yDir in ([-1, 0, 1]):
                    for xDir in ([-1, 0, 1]):
                        if (xDir == yDir == 0):
                            continue
                        if (xDir == -1 and x == 0):
                            continue
                        if (xDir == 1 and x == INNER_GRID_WIDTH-1):
                            continue
                        if (yDir == -1 and y == 0):
                            continue
                        if (yDir == 1 and y == INNER_GRID_HEIGHT-1):
                            continue
                        neighbors.append(self.currentFrame[y+yDir][x+xDir])
                aliveNeighbors = [x for x in neighbors if x > 0]
                cellLives = False

                # is alive and one or no neighbors
                if currentValue > 0 and len(aliveNeighbors) < 2:
                    cellLives = False

                # is alive and 2 or 3 alive neighbors
                if currentValue > 0 and (len(aliveNeighbors) == 2 or len(aliveNeighbors) == 3):
                    cellLives = True

                # is alive and more than 4 alive neighbors
                if currentValue > 0 and len(aliveNeighbors) >= 4:
                    cellLives = False

                # is dead cell and 3 alive neighbors
                if currentValue == 0 and len(aliveNeighbors) == 3:
                    cellLives = True

                self.nextFrame[y][x] = (25 if cellLives else 0)

        self.currentFrame = self.nextFrame
        self.nextFrame = [[0 for x in range(INNER_GRID_WIDTH)] for y in range(INNER_GRID_HEIGHT)]
        self.drawFrame()


seed(0)
lp = LaunchpadMiniMk3()
sim = GoLBoard(lp)
simRunning = False
playFrameDivider = playFrameDividerMax = 15

color = 0

def controlChange(msg):
    global color, simRunning, playFrameDividerMax
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
        if (button == CB_SESSION):
            simRunning = ~(simRunning)
            print("Simulation %s" % ("resume" if simRunning else "paused"))
            lp.SetPixel(4, 8, (21 if simRunning else 5))
        if (button == CB_DRUMS):
            sim.play()
        if (button == CB_KEYS):
            pass
        if (button == CB_USER): # CLEAR GRID
            for x in range(0, INNER_GRID_WIDTH):
                for y in range(0, INNER_GRID_HEIGHT):
                    lp.SetPixel(x, y, 0)
            sim.reset()
        if (button == 89): # SPEED IT UP
            if (playFrameDividerMax > 0):
                playFrameDividerMax -= 1
            print("Speed up %d" % playFrameDividerMax)
        if (button == 79):
            if (playFrameDividerMax < 50):
                playFrameDividerMax += 1

        if (color < 0):
            color = color + 128
        color = color % 128
        updateColorSignifier()

def buttonRelease(msg):
    global color, simRunning
    x = (msg.note % 10) - 1
    y = int(msg.note / 10) - 1
    print("BUTTON RELEASE x %d y %d" % (x, y), msg)

def buttonPress(msg):
    x = (msg.note % 10) - 1
    y = int(msg.note / 10) - 1
    sim.setCell(x, y)
    lp.SetPixel(x, y, color)
    print("BUTTON PRESS x %d, y %d" % (x, y))

def updateColorSignifier():
    lp.SetPixel(8, 8, color)
    lp.SetPixel(4, 8, (21 if simRunning else 5))

def main():
    global playFrameDivider
    # Register launchpad callbacks
    lp.onButtonPressCb = buttonPress
    lp.onButtonReleaseCb = buttonRelease
    lp.onControlChangeCb = controlChange
    lp.ClearGrid()
    lp.SelectLayout(LAYOUT_PROGRAMMER)
    updateColorSignifier()
    running = True
    while(running):
        try:
            if (simRunning):
                if (playFrameDivider == 0):
                    sim.play()
                    playFrameDivider = playFrameDividerMax
                else:
                    playFrameDivider -= 1
            lp.Poll()
            time.sleep(0.01)
        except KeyboardInterrupt:
            running = False
    lp.SelectLayout(LAYOUT_CUSTOM1)

if __name__ == "__main__":
    main()
