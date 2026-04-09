from psychopy import visual

def sec_to_fr(dur_s, rrate):
    # Seconds to frames
    return int(np.fix(dur_s * rrate))

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
        end=[topLeftCorner[0]+1, topLeftCorner[1]],
        interpolate=False,
        lineColor=pixelValue,
        colorSpace='rgb255',
        fillColor=None
)
    
    line.draw()
    # topLeftCorner = [-win.size[0]/2 + 0.5, win.size[1]/2 - 0.5]  # Adjusted to ensure the pixel is drawn at the top-left corner
    # pixelStim = visual.Rect(
    #     win=win,
    #     units='pix',
    #     width=1,
    #     height=1,
    #     pos=topLeftCorner,
    #     interpolate=False,
    #     lineColor=pixelValue,
    #     fillColor=pixelValue,
    #     colorSpace='rgb255'
    # )
    # pixelStim.draw()
    # if baseline:
    #     pixelStim.autoDraw = True  # Keep the pixel drawn across flips for baseline conditions


# def RGB2Trigger(color):
#     #helper function determines expected trigger from a given RGB 255 colour value
#     #return triggerVal
#     return int( (color[2]<<16)+(color[1]<<8)+color[0] ) 


# def Trigger2RGB(trigger):
#     #helper function determines pixel mode RGB 255 colour value based on 24-bit trigger (in decimal, base 10)  
#     # return [red, green, blue]
#     return [ trigger%256, (trigger>>8)%256, (trigger>>16)%256] 

def GB2trigger(color):
    G = color[1]
    B = color[2]

    return (B << 8) + G

def Trigger2GB(trigger):
    if not (0 <= trigger <= 65535):
        raise ValueError("Trigger must be between 0 and 65535.")

    G = trigger & 0xFF          # lower 8 bits
    B = (trigger >> 8) & 0xFF   # upper 8 bits

    return [0, G, B]

def print_trigger_info(device):
    line = device.getVideoLine()
    linevalue = GB2trigger([line[0][0], line[1][0], line[2][0]])
    print(f"Video line value: {linevalue}")  # Debugging output to check the video line value