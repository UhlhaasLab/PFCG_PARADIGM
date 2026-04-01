## Script to generate square stimuli, fixations and cues
    # Must change monitor specifications here (size, refresh rate etc.), also name of monitor
    # Scaling, visual angle, stimulus parameters

import os
# import ctypes
from psychopy import visual, core, monitors
# import numpy as np
# from PIL import Image, ImageDraw

# Set current directory
cwd_ = os.getcwd()
mainwd_ = os.path.dirname(cwd_)

#These are the settings for the monitor inside the cabinet 
viewing_distance_cm = 90    
screen_number       = 0
monitor_width_cm    = 53.7
monitor_size_pix    = [1920, 1200]

#Set monitor
monitor = monitors.Monitor("Sudring")
monitor.setWidth(monitor_width_cm)
monitor.setDistance(viewing_distance_cm)
monitor.setSizePix(monitor_size_pix)
monitor.save()

# define the window
win = visual.Window(monitor="Sudring", fullscr=True, screen=0, color=("#AAAAAA"), units="deg")


# Positioning a stimulus 2 degrees to the right of center
# The pos parameter takes [x, y]
#square_L = visual.Rect(win=win, units='deg', size=[0.4, 0.4], fillColor='#BBBBBB', pos=(-0.8, 0))
#square_C = visual.Rect(win=win, units='deg', size=[0.4, 0.4], fillColor='#BBBBBB', pos=(0, 0))
#square_R = visual.Rect(win=win, units='deg', size=[0.4, 0.4], fillColor='#000000', pos=(0.8, 0))
#
#square_L.draw()
#square_C.draw()
#square_R.draw()
#win.flip()
#filename = 'square_right.png'
#img_path = os.path.join(mainwd_, 'stimuli', 'square_right', filename)
#win.getMovieFrame()
#win.saveMovieFrames(img_path)
#
#square_L = visual.Rect(win=win, units='deg', size=[0.4, 0.4], fillColor='#000000', pos=(-0.8, 0))
#square_C = visual.Rect(win=win, units='deg', size=[0.4, 0.4], fillColor='#BBBBBB', pos=(0, 0))
#square_R = visual.Rect(win=win, units='deg', size=[0.4, 0.4], fillColor='#BBBBBB', pos=(0.8, 0))
#
#square_L.draw()
#square_C.draw()
#square_R.draw()
#win.flip()
#filename = 'square_left.png'
#img_path = os.path.join(mainwd_, 'stimuli', 'square_left', filename)
#win.getMovieFrame()
#win.saveMovieFrames(img_path)

# FIXATION
fixation_cue = visual.Circle(win=win, units='deg', size=[0.4, 0.4], fillColor='#BBBBBB', pos=(0, 0))
fixation_cue.draw()
win.flip()
filename = 'Fixation_Cuee.png'
win.getMovieFrame()
win.saveMovieFrames(os.path.join(mainwd_, 'stimuli', filename))

# CONG CUE
#cong_cue = visual.Rect(win=win, units='deg', size=[0.4, 0.4], fillColor='#3B7C22', pos=(0, 0))  # old from sara
cong_cue = visual.Circle(win=win, units='deg', size=[0.4, 0.4], fillColor='#005AB5', pos=(0, 0)) # blue
cong_cue.draw()
win.flip()
filename = 'cue_congg.png'
win.getMovieFrame()
win.saveMovieFrames(os.path.join(mainwd_, 'stimuli', filename))

# INCONG CUE
#incg_cue = visual.Rect(win=win, units='deg', size=[0.4, 0.4], fillColor='#E87032', pos=(0, 0)) # old from sara
incg_cue = visual.Circle(win=win, units='deg', size=[0.4, 0.4], fillColor='#DC3220', pos=(0, 0)) # red
incg_cue.draw()
win.flip()
filename = 'cue_incgg.png'
win.getMovieFrame()
win.saveMovieFrames(os.path.join(mainwd_, 'stimuli', filename))



win.close()
core.quit()