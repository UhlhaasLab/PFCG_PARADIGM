import os
# import serial
# import csv
import numpy as np
# from datetime import datetime
# import random
from psychopy import core, visual, event, monitors

from PFCG_cfg import stimwd, datawd, preload_stimuli
from pfcg_utils.utils_bottons import flush_button_buffer, read_button_press
from pfcg_utils.utils_stimuli import StimulusPresenter
from pfcg_utils.utils_trials import get_block_trialtypes, get_block_cuetypes
# from pfcg_utils.buttons import collect_response, flush_buttons
# from pfcg_utils.PixelMode import drawPixelModeTrigger,  print_trigger_info, GB2trigger, Trigger2GB
from pypixxlib.datapixx import DATAPixx3


device      = DATAPixx3()

# enable pixel mode once
device.dout.enablePixelModeGB()
device.updateRegisterCache() 

# Initialize button
myLog = device.din.setDinLog(12e6, 1000)
device.din.startDinLog()
device.updateRegisterCache()

event.clearEvents() 
flush_button_buffer(device, myLog)


# ==================== MONITOR ==================== #
# ==================== MONITOR ==================== #
TestingPort = True      # True if on a laptop. 

if TestingPort:
    viewing_distance_cm = 57.3    
    monitor_width_cm    = 52.7
    monitor_size_pix    = [1280,720]
    monitor_name        = "testMonitor"
    monitor_rr = 60
    screen_num = 0  # Change this to the appropriate screen number for the testing setup
    
else:   #----------------------> # change OPM/EEG lab port settings
    viewing_distance_cm = 90    
    monitor_width_cm    = 53.7
    monitor_size_pix    = [1920, 1080]
    monitor_name        = "OPM-lab"
    monitor_rr = 120
    screen_num = 2  # Change this to the appropriate screen number for the OPM lab setup
    
""" change the else loop if in EEG Lab Suedring to:
else:
    # Lab Settings (Sudring)
    # Change the size depending on the monitor in question
    viewing_distance_cm = 90    
    monitor_width_cm    = 53.7
    monitor_size_pix    = [1920, 1200]
    monitor_name        = "Sudring"
"""

# Apply Monitor Settings
monitor = monitors.Monitor(monitor_name)
monitor.setWidth(monitor_width_cm)
monitor.setDistance(viewing_distance_cm)
monitor.setSizePix(monitor_size_pix)
monitor.save()

# win = visual.Window(monitor=monitor, fullscr=True, color=("#AAAAAA"), units="deg") # Create the window with aforementioned monitor
win = visual.Window( monitor=monitor_name, color=("#AAAAAA"), units="pix",screen=screen_num, size = monitor_size_pix, allowGUI=False, fullscr=True) # Create the window with aforementioned monitor
win.mouseVisible = False # Hide mouse

# Set participant ID for loading stimuli
participant_id = 'Practice'
participant_dir = os.path.join(datawd, participant_id)

# import cues and stimuli
stimuli = preload_stimuli(win, stimwd, participant_dir)

rt_clock = core.Clock()
presenter = StimulusPresenter(window=win, triggers=True)

## Defining Variables                   
# symbol_offset = 1.5

## Setting up the practice
BLOCK = 0               
trialtype = get_block_trialtypes(BLOCK, participant_id, datawd)
cuetype = get_block_cuetypes(BLOCK, participant_id, datawd)
ntrials = len(trialtype)

group_size = 5
num_groups = ntrials // group_size

# Initialize accuracy tracking
correct_responses = 0
total_trials = 0

# Iteration for the mini-blocks
for group_idx in range(num_groups):
    
    # Get info each iteration of group
    start_idx = group_idx * group_size
    end_idx = start_idx + group_size

    cueid = cuetype[start_idx]
    
    if group_idx == 0:

        stimuli['welcome_practice'].draw()
        win.flip()
        button_name = None
        while button_name != 'blue':  # Wait until a button is pressed
            button_name, _ = read_button_press(device, myLog)
        rt_clock.reset()
        event.clearEvents()
        flush_button_buffer(device, myLog)  # Clear any old button presses from the buffer
  
        # Practice instructions
        stimuli['instructions_1'].draw()
        win.flip()
        button_name = None
        while button_name !=  'blue':  # Wait until a button is pressed
            button_name, _ = read_button_press(device, myLog)
        rt_clock.reset()
        event.clearEvents()
        flush_button_buffer(device, myLog)  # Clear any old button presses from the buffer

        stimuli['instructions_2'].draw()
        win.flip()
        button_name = None
        while button_name != 'blue':  # Wait until a button is pressed
            button_name, _ = read_button_press(device, myLog)
        rt_clock.reset()
        event.clearEvents()
        flush_button_buffer(device, myLog)  # Clear any old button presses from the buffer
        
        stimuli['begin_text'].draw()
        win.flip()
        button_name = None
        while button_name != 'blue':  # Wait until a button is pressed
            button_name, _ = read_button_press(device, myLog)
        rt_clock.reset()
        event.clearEvents()
        flush_button_buffer(device, myLog)  # Clear any old button presses from the buffer

    # Task begins here for each mini-block
    
    # Show baseline cue for 500ms
    stimuli['cue_baseline'].draw()
    # drawPixelModeTrigger(win, Trigger2GB(10)) 
    win.flip()
    core.wait(0.5)
    
    # Show fixation for 2500ms
    stimuli['Fix_Dot'].draw()
    win.flip()                           
    core.wait(2.5)

    # Show cue_cong or cue_incg for 500ms
    cue_stimulus = presenter.get_cue_stimulus(stimuli, cueid)
    cue_trigger_code = presenter.get_cue_trigger_code(cueid)
    presenter.present_cue(cue_stimulus, trigger_code=cue_trigger_code, frame_rate=monitor_rr, device=device)

    # Show fixation. Jitter between 1400-1600ms
    jitter = np.random.choice(np.arange(1.4, 1.61, 0.01))
    jitter = round(jitter, 2)
    post_cue_jitter = presenter.present_fixation(stimuli['Fix_Dot'], duration=jitter, frame_rate=monitor_rr)

    # Present 5 trials
    for trial_idx in range(start_idx, end_idx):
        trialid = trialtype[trial_idx]
        arrow_stimulus = presenter.target_type(stimuli, trialid)
        
        # Calculate position within the 5-trial sequence (1-5)
        trial_position = (trial_idx - start_idx) + 1
        target_trigger_code = presenter.get_target_trigger_code(trialid, trial_position)

        event.clearEvents()

        # Generate jitter
        jitter = np.random.choice(np.arange(1.4, 1.61, 0.01))
        jitter = round(jitter, 2)

        # Send trigger at Flip
        arrow_stimulus.draw()
        # win.flip()
        # if target_trigger_code is not None:
        #     drawPixelModeTrigger(win, Trigger2GB(target_trigger_code))  # send trigger using pixel mode


        timer = core.Clock()
        flip_marks = {}
        device.updateRegisterCache()
        win.callOnFlip(lambda: flip_marks.setdefault('t0_dev', device.getTime()))
        win.callOnFlip(timer.reset)
        win.flip()
        
        # Initialize response variables
        t_0_v = flip_marks['t0_dev']
        key_pressed = None
        reaction_time = None
        reaction_time_vpixx = None
        arrow_duration = 0.5
        response_deadline = arrow_duration + jitter

        flush_button_buffer(device, myLog)  # Clear any old button presses from the buffer
   
    
        # Monitor for responses during target presentation (0.5s)
        while timer.getTime() < arrow_duration:
            # keys = event.getKeys(keyList=['num_7', 'num_9', 'escape'])

            button_name, timestamp = read_button_press(device, myLog)  # Check for button presses
            if button_name is not None:
                key_pressed = button_name
                reaction_time = timer.getTime()
                reaction_time_vpixx = timestamp - t_0_v  # Calculate reaction time based on VPixx timestamp

                # response_trigger_code = presenter.get_response_trigger_code(key_pressed)
                # presenter.send_trigger_opm(response_trigger_code)  # send response trigger using pixel mode
                # presenter.win.flip()  # Ensure the trigger is sent immediately

        # Show fixation
        stimuli['Fix_Dot'].draw()
        win.callOnFlip(timer.reset)  # Mark fixation onset time
        win.flip()
        
        # Continue monitoring during fixation if no response yet
        if key_pressed is None:
            while timer.getTime() < jitter:
                # flush_button_buffer(device, myLog)  # Clear any old button presses from the buffer
                button_name, timestamp = read_button_press(device, myLog)  # Check for button presses
                if button_name is not None:
                    key_pressed = button_name
                    # RT during fixation = 0.5 + time into fixation
                    reaction_time = arrow_duration + timer.getTime()
                    reaction_time_vpixx = timestamp - t_0_v  # Calculate reaction time based on VPixx timestamp
                    # response_trigger_code = presenter.get_response_trigger_code(key_pressed)
                    # presenter.send_trigger_opm(response_trigger_code)
                    # presenter.win.flip()  # Ensure the trigger is sent immediately

            # Wait for any remaining fixation time
            remaining_time = jitter - timer.getTime()
            if remaining_time > 0:
                core.wait(remaining_time)
                
        else:
            # Response already given during target, just wait the full jitter duration
            core.wait(jitter)
            
        # Determine trial info for CSV
        correct_key = ''
        trial_num = trial_idx + 1  # or use your CSV's trial column if loaded
        if trialid == 0:
            trialtype_string = 'right_cong'
            correct_key = 'red'
        elif trialid == 1:
            trialtype_string = 'left_cong'
            correct_key = 'green'
        elif trialid == 2:
            trialtype_string = 'right_incg'
            correct_key = 'green'
        elif trialid == 3:
            trialtype_string = 'left_incg'
            correct_key = 'red'
        else:
            trialtype_string = 'unknown'
            correct_key = 'unknown'
        cuetype_val = cuetype[trial_idx]
        cuetype_string = 'cong' if cuetype_val == 1 else 'incg'
        block_num = BLOCK
        
        # Check if the pressed key matches the correct key
        is_resp_corr = []
        if key_pressed == correct_key:
            is_resp_corr = 1
            correct_responses += 1
        else:
            is_resp_corr = 0
        total_trials += 1
        
        """
        # Johanna: the following lines were slightely different than in the PFCG_paradigm.py, so i commented them out and copied the same lines from the paradigm.py into here.
        # if this was different on purpose, just delete the above and use this.
        if not key_pressed:
            while timer.getTime() < response_deadline:
                keys = event.getKeys(keyList=['num_7', 'num_9', 'escape'])
                if keys:
                    key_pressed = keys[0]
                    # RT during fixation = 0.5 + time into fixation
                    reaction_time = timer.getTime()
                    response_trigger_code = presenter.get_response_trigger_code(key_pressed)
                    presenter.send_trigger(response_trigger_code)
                    if key_pressed == 'escape':
                        core.quit()
                    break

        # Wait for remaining fixation time
        remaining_time = response_deadline - timer.getTime()
        if remaining_time > 0:
            core.wait(remaining_time)
            
        # Determine correct key for accuracy tracking
        correct_key = ''
        if trialid == 0:
            correct_key = 'num_9'
        elif trialid == 1:
            correct_key = 'num_7'
        elif trialid == 2:
            correct_key = 'num_7'
        elif trialid == 3:
            correct_key = 'num_9'

        # Track accuracy
        if key_pressed == correct_key:
            correct_responses += 1
        total_trials += 1
        """

# Calculate and display accuracy
if total_trials > 0:
    accuracy_percentage = (correct_responses / total_trials) * 100
else:
    accuracy_percentage = 0

text_DE=f'Übung abgeschlossen!\n\nSie waren bei {accuracy_percentage:.1f}% der Versuche korrekt.\n\nDrücken Sie den blauen Knopf, um fortzufahren.'

# Create accuracy feedback text
accuracy_text = visual.TextStim(
    win,text_DE,
    color='white',
    height=1,
    pos=(0, 0),
    units='deg',
    wrapWidth=60
)

accuracy_text.draw()
win.flip()
core.wait(10)
win.close()
core.quit()