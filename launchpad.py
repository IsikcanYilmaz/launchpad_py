#!/usr/bin/python3

from common import *
import mido
import time

class Pixel:
    def __init__(self):
        pass

class LaunchpadMiniMk3:
    def __init__(self):
        self.inport = mido.open_input('Launchpad Mini MK3:Launchpad Mini MK3 MIDI 2 20:1')
        self.outport = mido.open_output('Launchpad Mini MK3:Launchpad Mini MK3 MIDI 2 20:1')
        self.grid = [[Pixel() for x in range(GRID_WIDTH)] for y in range(GRID_HEIGHT)]

        self.onButtonPressCb = None
        self.onButtonReleaseCb = None
        self.onControlChangeCb = None

    def PrintGrid(self):
        for y in range(0, GRID_HEIGHT):
            print(self.grid[GRID_HEIGHT-1-y])

    def DeviceInquiryMessage(self):
        msg = mido.Message('sysex', data=[0x7e, 0x7f, 0x06, 0x01])
        self.outport.send(msg)
        resp = inport.receive()
        print(resp)

    def SelectLayout(self, layout):
        msg = mido.Message('sysex', data=[0x00, 0x20, 0x29, 0x02, 0x0D, 0x00, layout])
        self.outport.send(msg)

    def GetPixel(self, x, y):
        return self.grid[y][x]

    def SetPixel(self, x, y, color):
        msg = mido.Message('note_on', note=((y+1)*10) + (x+1) , velocity=color)
        self.outport.send(msg)
        self.grid[y][x] = color

    def SetPixelRgb(self, x, y, r, g, b):
        pass

    def ClearGrid(self):
        for x in range(0, GRID_WIDTH):
            for y in range(0, GRID_HEIGHT):
                self.SetPixel(x, y, 0)

    def Poll(self):
        msg = self.inport.poll()
        if (msg):
            if (msg.type == 'note_on' and self.onButtonPressCb):
                self.onButtonPressCb(msg)
            if (msg.type == 'control_change' and self.onButtonPressCb):
                self.onControlChangeCb(msg)
            if (msg.type == 'note_off' and self.onButtonReleaseCb):
                self.onButtonReleaseCb(msg)

    def LpService(self):
        pass

    def LpServiceStart(self):
        pass



def main():
    lp = LaunchpadMiniMk3()
    lp.SelectLayout(LAYOUT_PROGRAMMER)
    lp.SetPixel(3, 7, 0)
    return
    i = 0
    j = 0
    while(True):
        for k in range(0, 9):
            lp.SetPixel(k, i%9, j%128)
        time.sleep(0.03)
        i += 1
        j += 1
        lp.Poll()


if __name__ == "__main__":
    main()
