#!/usr/bin/python3

from launchpad import *
from random import *
from common import *
import colorsys
import time

lp = LaunchpadMiniMk3(pickPortInteractive())
grid = None
pressedButtons = []
fireworks = []

class Firework:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 0
        self.expansionRate = 0.01
        self.maxRadius = 20
        self.alive = True

    def release(self):
        pass

    def update(self):
        self.radius += self.expansionRate
        

class Grid:
    def __init__(self):
        self.gridArr = [[0 for j in range(0, GRID_HEIGHT)] for i in range(0, GRID_WIDTH)]

    def getCellValue(self, x, y):
        return self.gridArr[x][y]

    def setCellValue(self, x, y, val):
        self.gridArr[x][y] = val

    def printGridInt(self):
        for j in range(0, GRID_HEIGHT):
            print(["%04d" % int(i) for i in self.gridArr[j]])
        print("\n")
    
    def update(self):
        for f in fireworks:
            f.update()

    def draw(self):
        pass



def buttonRelease(msg):
    x = int(msg.note % 10) - 1
    y = int(msg.note / 10) - 1
    for i in range(0, len(pressedButtons)):
        if (pressedButtons[i][0] == x and pressedButtons[i][1] == y):
            del(pressedButtons[i])
            break
    print("BUTTON RELEASE", msg)

def controlChange(msg):
    print("CONTROL CHANGE", msg)

def buttonPress(msg):
    x = int(msg.note % 10) - 1
    y = int(msg.note / 10) - 1
    pressedButtons.append((x, y))
    print("BUTTON PRESS x %d, y %d" % (x, y))

def processButtonPresses():
    global grid
    for b in pressedButtons:
        currVal = grid.getCellValue(b[0], b[1])
        newVal = currVal + 1000
        grid.setCellValue(b[0], b[1], newVal)

def main():
    global grid
    # Register launchpad callbacks
    lp.onButtonPressCb = buttonPress
    lp.onButtonReleaseCb = buttonRelease
    lp.onControlChangeCb = controlChange
    lp.ClearGrid()
    lp.SelectLayout(LAYOUT_PROGRAMMER)
    grid = Grid()
    running = True
    while(running):
        try:
            lp.Poll()
            processButtonPresses()
            grid.update()
            grid.draw()
            time.sleep(0.04)
        except KeyboardInterrupt:
            running = False
    lp.SelectLayout(LAYOUT_CUSTOM1)

if __name__ == "__main__":
    main()
