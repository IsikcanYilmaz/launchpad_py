#!/usr/bin/python3

from common import *
import mido
import time
import colorsys

H_MAX = 360
S_MAX = 100
V_MAX = 100

# Pixel Class
# - Can be in "Preset color" mode or "RGB" mode. The first is a value from 0 to 127. Refer to color palette in the "Launchpad programmers manual".
# The second is rgb mode, 3 bytes to express a pixel. The difference between these modes is the ease of lighting up a pixel using the preset colors, since it
# takes one "note on" midi packet to light a pixel with a preset color. Its bit longer than that with the rgbs.
# - One can set mode explicitly via SetMode() or using either SetRGB or SetPreset will change the mode accordingly anyway.
class Pixel:
    def __init__(self):
        self.presetColorVal = 0
        self.r = 0
        self.g = 0
        self.b = 0

    def SetRgb(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def SetPreset(self, val):
        self.presetColorVal = val

    def GetColor(self):
        return self.presetColorVal

    def GetColorRgb(self):
        return (self.r, self.g, self.b)

# LaunchpadMiniMk3 Class
# - This holds the main functionality that controls the LPMiniMk3. It implements whats described in the lpminimk3 programmers manual.
class LaunchpadMiniMk3:
    def __init__(self, portstr):
        self.inport = mido.open_input(portstr)
        self.outport = mido.open_output(portstr)
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
        self.GetPixel(x, y).SetPreset(color)
        msg = mido.Message('note_on', note=((y+1)*10) + (x+1) , velocity=color)
        self.outport.send(msg)

    def SetPixelRgb(self, x, y, r, g, b):
        self.GetPixel(x, y).SetRgb(r, g, b)
        ledIdx = ((y+1) * 10) + (x+1)
        r = (r if r<128 else 127)
        g = (g if g<128 else 127)
        b = (b if b<128 else 127)
        data=[0x00, 0x20, 0x29, 0x02, 0x0D, 0x03]
        data.append(0x03)
        data.append(ledIdx)
        data.extend([r, g, b])
        msg = mido.Message('sysex', data = data)
        self.outport.send(msg)

    def ClearGrid(self):
        for x in range(0, GRID_WIDTH):
            for y in range(0, GRID_HEIGHT):
                self.SetPixel(x, y, 0)

    def DisplayText(self, text, loop=False, speed=5, color=5):
        if (speed > 0xff):
            print("Bad speed argument")
            return
        if (color > 0xff):
            print("Bad color argument")
            return
        data = [0x00, 0x20, 0x29, 0x02, 0x0D, 0x07]
        data.append(0x00 if loop == False else 0x01)
        data.append(speed)
        data.append(0x00)
        data.append(color)
        data.extend([i for i in bytearray(text.encode('utf-8'))])
        msg = mido.Message('sysex', data=data)
        self.outport.send(msg)

    def Poll(self):
        msg = self.inport.poll()
        if (msg):
            if (msg.type == 'note_on' and msg.velocity == 127 and self.onButtonPressCb):
                self.onButtonPressCb(msg)
            if (msg.type == 'control_change' and self.onButtonPressCb):
                self.onControlChangeCb(msg)
            if (msg.type == 'note_on' and msg.velocity == 0 and self.onButtonReleaseCb):
                self.onButtonReleaseCb(msg)

    def LpService(self):
        pass

    def LpServiceStart(self):
        pass

def pickPortInteractive():
    print('[*] Select port. (Working example: %s)' % ('Launchpad Mini MK3:Launchpad Mini MK3 MIDI 2 24:1'))
    inputNames = mido.get_input_names()
    for i in range(0, len(inputNames)):
        print(i, inputNames[i])
    selection = int(input())
    print(selection, inputNames[selection])
    return inputNames[selection]

def main():
    lp = LaunchpadMiniMk3(pickPortInteractive())
    lp.SelectLayout(LAYOUT_PROGRAMMER)
    # lp.DisplayText("Hello Whorl", loop=False, speed=10, color=57)
    h = 0
    s = 70
    v = 100
    while(True):
        for i in range(0, 9):
            test_color = colorsys.hsv_to_rgb((10*i+h)/H_MAX, s/S_MAX, v/V_MAX)
            test_color = [i * 127 for i in test_color]
            for j in range(0, 9):
                lp.SetPixelRgb(i, j, int(test_color[0]), int(test_color[1]), int(test_color[2]))
        h += 1
        time.sleep(0.01)

    input()
    lp.SelectLayout(LAYOUT_SESSION)

if __name__ == "__main__":
    main()
