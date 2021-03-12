#!/usr/bin/python3

from launchpad import *
from random import *
from common import *
import numpy as np
import matplotlib.pyplot as plt
import colorsys
import time

lp = LaunchpadMiniMk3(pickPortInteractive())
grid = None
pressedButtons = []


# setup the figure and axes
# fig = plt.figure(figsize=(8, 3))
# ax1 = fig.add_subplot(121, projection='3d')
# ax2 = fig.add_subplot(122, projection='3d')

# fake data
# _x = np.arange(4)
# _y = np.arange(5)
# _xx, _yy = np.meshgrid(_x, _y)
# x, y = _xx.ravel(), _yy.ravel()

# top = x + y
# bottom = np.zeros_like(top)
# width = depth = 1

# ax1.bar3d(x, y, bottom, width, depth, top, shade=True)
# ax1.set_title('Shaded')

# ax2.bar3d(x, y, bottom, width, depth, top, shade=False)
# ax2.set_title('Not Shaded')

# plt.show()


class Plotter:
    def __init__(self):
        pass

class Grid:
    def __init__(self):
        self.gridArr = [[0 for j in range(0, GRID_HEIGHT)] for i in range(0, GRID_WIDTH)]
        self.decay = 1

    def getCellValue(self, x, y):
        return self.gridArr[x][y]

    def setCellValue(self, x, y, val):
        self.gridArr[x][y] = val

    def printGridInt(self):
        for j in range(0, GRID_HEIGHT):
            print(["%04d" % int(i) for i in self.gridArr[j]])
        print("\n")
    
    def update(self):
        newGridArr = [[0 for j in range(0, GRID_HEIGHT)] for i in range(0, GRID_WIDTH)]
        for i in range(0, GRID_WIDTH):
            for j in range(0, GRID_HEIGHT):
               neighborVals = []
               neighborVals.append(self.getCellValue((i+1)%GRID_WIDTH, j))
               neighborVals.append(self.getCellValue((i-1)%GRID_WIDTH, j))
               neighborVals.append(self.getCellValue(i, (j+1)%GRID_HEIGHT))
               neighborVals.append(self.getCellValue(i, (j-1)%GRID_HEIGHT))
               neighborVals.append(self.getCellValue((i+1)%GRID_WIDTH, (j+1)%GRID_HEIGHT))
               neighborVals.append(self.getCellValue((i-1)%GRID_WIDTH, (j+1)%GRID_HEIGHT))
               neighborVals.append(self.getCellValue((i+1)%GRID_HEIGHT, (j-1)%GRID_HEIGHT))
               neighborVals.append(self.getCellValue((i-1)%GRID_HEIGHT, (j-1)%GRID_HEIGHT))
               avg = sum(neighborVals)/len(neighborVals)
               diff = self.getCellValue(i, j) - avg
               # print(int(diff))
               decay = 0#(avg / 100)
               newVal = avg + (-1 * decay if avg >= 0 else decay)
               # newVal = avg - self.decay
               # newVal = (0 if newVal < 0 else newVal)
               # newVal = (500 if newVal > 500 else newVal)
               newGridArr[i][j] = newVal
        self.gridArr = newGridArr

    def draw(self):
        baseH = 200
        baseS = 0
        baseV = 100
        for i in range(0, GRID_WIDTH):
            for j in range(0, GRID_HEIGHT):
                h = baseH + (self.getCellValue(i, j) / 2) / 2
                # h = (3*H_MAX if h > 3*H_MAX else h)
                s = baseS + self.getCellValue(i,j) / 5
                s = (100 if s > 100 else s)
                v = baseV
                # v = self.getCellValue(i,j) * 100 / 500
                # v = (100 if v > 100 else v)
                cellColor = colorsys.hsv_to_rgb((h)/H_MAX, s/S_MAX, v/V_MAX)
                cellColor = [i * 127 for i in cellColor]
                lp.SetPixelRgb(i, j, int(cellColor[0]), int(cellColor[1]), int(cellColor[2]))



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
