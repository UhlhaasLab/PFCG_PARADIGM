# everywhere with "ADAPT" needs to be changed
# adapt keys/buttons etc to OPM: correct_key defined here and in utils_trials

import os
import serial
import csv
import numpy as np
from datetime import datetime
import random
from psychopy import logging, prefs, core, visual, event, monitors

from PFCG_cfg import stimwd, datawd, preload_stimuli
from pfcg_utils.utils_bottons import flush_button_buffer,cleanup_and_exit, read_button_press, stopButtons
from pfcg_utils.utils_stimuli import StimulusPresenter, sec_to_fr
from pfcg_utils.utils_trials import get_block_trialtypes, get_block_cuetypes
from pfcg_utils.buttons import collect_response, flush_buttons
from pfcg_utils.PixelMode import drawPixelModeTrigger, RGB2Trigger, Trigger2RGB
from pypixxlib.datapixx import DATAPixx3
# ==================== VPIXX ==================== #
# triggers
TRIG_left  = 3  # 00000011
TRIG_right = 4  # 00000100 
TRIG_white = 5  # 00000101  

# Working codes in Lab maestro Simulator
BUTTON_CODES = {65527:'blue', 65533:'yellow', 65534:'red', 65531:'green', 65519:'white'}
# , 65535:'button release'
exitButton  = 65519 # white button code in Lab Maestro Simulator
# startbutton = ['65534', '65531'] # red and green button codes in Lab Maestro Simulator (both can be used to start the task, but only one should be used to end it, to avoid accidental quitting during the task) --- ADAPT if needed for OPM lab
# Button codes in MSR
#BUTTON_CODES = { 65528: 'blue', 65522: 'yellow', 65521: 'red', 65524: 'green', 65520: 'button release' }

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
TestingPort = True      # True if on a laptop. False if in EEG-lab/Sudring ------> ADAPT (also in utils_stimuly.py)

if TestingPort:
    viewing_distance_cm = 50    
    monitor_width_cm    = 34.5
    monitor_size_pix    = [1920, 1080]
    monitor_name        = "testMonitor"
    
else:   #----------------------> # change OPM/EEG lab port settings
    viewing_distance_cm = 90    
    monitor_width_cm    = 53.7
    monitor_size_pix    = [1920, 1200]
    monitor_name        = "OPM-lab"
    
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

win = visual.Window(monitor=monitor, fullscr=True, color=("#AAAAAA"), units="deg") # Create the window with aforementioned monitor
win.mouseVisible = False # Hide mouse

# ==================== SET PARTICIPANT ID ==================== #
date_str = datetime.now().strftime("%Y-%m-%d")
participant_id = 'Erfan'    # -----------------------------------------------> ADAPT
participant_dir = os.path.join(datawd, participant_id)

# ==================== IMPORT STIMULI ==================== #
stimuli = preload_stimuli(win, stimwd, participant_dir) # for modifying relevant stimuli, see utils_stimuli

rt_clock = core.Clock()
rt_clock2 = core.Clock()
onsettime = rt_clock2.getTime()
presenter = StimulusPresenter(window=win, exptimer=rt_clock2, triggers=True)

# ==================== EXPORT LOG FILE ==================== #
# Create file path for CSV log
datafile_path = os.path.join(participant_dir, f"{participant_id}_behaviour_{date_str}.csv")

# Open and write headers if file doesn't exist
if not os.path.exists(datafile_path):
    with open(datafile_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['block', 'trial', 'trialtype', 'trialtype_string', 'cuetype', 'cuetype_string', 'correct_key', 'key_pressed','is_resp_corr', 'reaction_time'])

# ==================== EXPERIMENT ==================== #
symbol_offset = 1.5 # sets degrees from the centre --------------------------> is this OK also for the OPM lab

BLOCK = 1   # ------------------------------------------------> ADAPT

trialtype = get_block_trialtypes(BLOCK, participant_id, datawd)
cuetype = get_block_cuetypes(BLOCK, participant_id, datawd)
ntrials = len(trialtype)

group_size = 5          # if trial number is changed, change number here, and also generate a new master_blocks.csv using data\PFCG_change-trial-number_csv.py
num_groups = ntrials // group_size  # 8 mini blocks of 4 gratings grouped by congruency as given by the cue

# Initialize accuracy tracking
correct_responses = 0
total_trials = 0

# Iteration for the mini-blocks
for group_idx in range(num_groups):
    
    # Get info each iteration of group
    start_idx = group_idx * group_size
    end_idx = start_idx + group_size

    cueid = cuetype[start_idx]  # Use cuetype from first trial in group
    
    if group_idx == 0:
        stimuli['welcome_text'].draw()
        win.flip()
        # get the button press
        
        button_name = stopButtons(BUTTON_CODES.keys())  # Wait for either start or exit button press
        # print(f"Button pressed: {button_name}")
        if button_name == exitButton:
            core.quit()
        rt_clock.reset()
        event.clearEvents()
        
        stimuli['begin_text'].draw()
        win.flip()

        button_name = stopButtons(BUTTON_CODES.keys())  # Wait for either start or exit button press

        if button_name == exitButton:
            core.quit()
        rt_clock.reset()
        event.clearEvents()
    # Task begins here for each mini-block
    
    # Show baseline cue for 500ms
    # win.callOnFlip(presenter.send_trigger, 11)
    win.callOnFlip(drawPixelModeTrigger, win, Trigger2RGB(10))  # send trigger using pixel mode
    stimuli['cue_baseline'].draw()
    win.flip()
    core.wait(0.5)
    
    # Show fixation for 2500ms
    # win.callOnFlip(presenter.send_trigger, 9)  # fixation trigger
    win.callOnFlip(drawPixelModeTrigger, win, Trigger2RGB(9))
    stimuli['Fix_Dot'].draw()
    win.flip()
    core.wait(2.5)

    # Show cue_cong or cue_incg for 500ms
    cue_stimulus = presenter.get_cue_stimulus(stimuli, cueid)
    cue_trigger_code = presenter.get_cue_trigger_code(cueid)
    win.callOnFlip(presenter.send_trigger, cue_trigger_code)  # send trigger at flip
    presenter.present_cue(cue_stimulus, trigger_code=cue_trigger_code)

    # Show fixation. Jitter between 1400-1600ms
    jitter = np.random.choice(np.arange(1.4, 1.61, 0.01))
    jitter = round(jitter, 2)
    win.callOnFlip(presenter.send_trigger, 9)    # send fixation trigger at flip
    post_cue_jitter = presenter.present_fixation(stimuli['Fix_Dot'], duration=jitter)

    # Present 5 trials of gratings
    # start_idx and end_idx calling the appropriate row in the data (AKA conditions) file
    for trial_idx in range(start_idx, end_idx):
        trialid = trialtype[trial_idx]
        arrow_stimulus = presenter.target_type(stimuli, trialid)
        
        # Calculate position within the 5-trial sequence (1-5)
        trial_position = (trial_idx - start_idx) + 1
        target_trigger_code = presenter.get_target_trigger_code(trialid, trial_position)
        
        event.clearEvents()
        
        # Generate jitter for fixation duration (1.4-1.6s)
        jitter = np.random.choice(np.arange(1.4, 1.61, 0.01))
        jitter = round(jitter, 2)
        
        # Send trigger at Flip
        if target_trigger_code is not None:
            # win.callOnFlip(presenter.send_trigger, target_trigger_code)
            win.callOnFlip(drawPixelModeTrigger, win, Trigger2RGB(target_trigger_code))
        arrow_stimulus.draw()
        win.flip()
        
        timer = core.Clock()
        
        # Initialize response variables
        key_pressed = None
        reaction_time = None
        arrow_duration = 0.5
        response_deadline = arrow_duration + jitter
        
        # Monitor for responses during target presentation (0.5s)
        while timer.getTime() < arrow_duration:
            # keys = event.getKeys(keyList=['num_7', 'num_9', 'escape'])
            button_name, timestamp = read_button_press(device, myLog)  # Check for button presses
            if button_name:
                key_pressed = button_name
                reaction_time = timer.getTime()
                response_trigger_code = presenter.get_response_trigger_code(key_pressed)
                # presenter.send_trigger(response_trigger_code)
                drawPixelModeTrigger(win, Trigger2RGB(response_trigger_code))  # send response trigger using pixel mode
                if key_pressed == exitButton:
                    core.quit()
                break
                
        # Show fixation
        #win.callOnFlip(presenter.send_trigger, 9)    # johanna commented this out on request of tineke
        stimuli['Fix_Dot'].draw()
        win.flip()
        
        timer = core.Clock()  # Reset timer for fixation period
        
        # Continue monitoring during fixation if no response yet
        if not key_pressed:
            while timer.getTime() < jitter:
                button_name, timestamp = read_button_press(device, myLog)  # Check for button presses
                if button_name:
                    key_pressed = button_name
                    # RT during fixation = 0.5 + time into fixation
                    reaction_time = arrow_duration + timer.getTime()
                    response_trigger_code = presenter.get_response_trigger_code(key_pressed)
                    presenter.send_trigger(response_trigger_code)
                    if key_pressed == exitButton:
                        core.quit()
                    break
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
        
        # Write to CSV
        with open(datafile_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                block_num,      # block
                trial_num,      # trial
                trialid,        # trialtype (shows 0,1,2,3)
                trialtype_string,  # trialtype_string (shows left_incg, right_cong, etc.)
                cuetype_val,    # cuetype (shows 0 or 1)
                cuetype_string, # cuetype_string (shows incg or cong)
                correct_key,    # correct answer
                key_pressed,    # key_pressed
                is_resp_corr,   # correct
                reaction_time,  # reaction time
            ])

# Calculate and display accuracy
if total_trials > 0:
    accuracy_percentage = (correct_responses / total_trials) * 100
else:
    accuracy_percentage = 0

# Create accuracy feedback text
accuracy_text = visual.TextStim(
    win,
    text=f'Block {BLOCK}/10 is now complete. \n\nYou were correct on {accuracy_percentage:.1f}% of trials.\n\nThank you for your participation!',
    color='white',
    height=1,
    pos=(0, 0),
    units='deg',
    wrapWidth=60
)

accuracy_text.draw()
win.flip()
core.wait(10)