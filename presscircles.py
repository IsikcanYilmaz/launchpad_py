#!/usr/bin/python3

from launchpad import *
import time

lp = LaunchpadMiniMk3()

color = 0

mirrormodes = {'fourway' : False}

def buttonRelease(msg):
    print("BUTTON RELEASE", msg)

def controlChange(msg):
    global color
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
            mirrormodes['fourway'] = not mirrormodes['fourway']
            lp.SetPixel(4, 8, (21 if mirrormodes['fourway'] else 0))
        if (button == CB_DRUMS):
            pass
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
    if (mirrormodes['fourway']):
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
            lp.Poll()
            time.sleep(0.01)
        except KeyboardInterrupt:
            running = False
    lp.SelectLayout(LAYOUT_CUSTOM1)

if __name__ == "__main__":
    main()
