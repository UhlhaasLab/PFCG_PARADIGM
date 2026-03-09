from psychopy import visual

def drawPixelModeTrigger(win, pixelValue):
    #takes a pixel colour and draws it as a single pixel in the top left corner of the window
    #window must cover top left of screen to work
    #interpolate must be set to FALSE before color is set
    #call this just before flip to ensure pixel is drawn over other stimuli

    topLeftCorner = [-win.size[0]/2, win.size[1]/2]
    line = visual.Line(
        win=win,
        units='pix',
        start=topLeftCorner,
        end=[topLeftCorner[0]+10, topLeftCorner[1]],
        interpolate=False,
        lineColor=pixelValue,
        colorSpace='rgb255',
        fillColor=None
)
    line.draw()


def RGB2Trigger(color):
    #helper function determines expected trigger from a given RGB 255 colour value
    #return triggerVal
    return int( (color[2]<<16)+(color[1]<<8)+color[0] ) 


def Trigger2RGB(trigger):
    #helper function determines pixel mode RGB 255 colour value based on 24-bit trigger (in decimal, base 10)  
    # return [red, green, blue]
    return [ trigger%256, (trigger>>8)%256, (trigger>>16)%256] 
