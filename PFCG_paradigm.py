import os
import csv
import numpy as np
import argparse
from datetime import datetime
from psychopy import core, visual, event, monitors

from PFCG_cfg import stimwd, datawd, preload_stimuli
from pfcg_utils.utils_bottons import flush_button_buffer,cleanup_and_exit, read_button_press
from pfcg_utils.utils_stimuli import StimulusPresenter
from pfcg_utils.utils_trials import get_block_trialtypes, get_block_cuetypes, shuffle_blocks
from pfcg_utils.PixelMode import drawPixelModeTrigger, print_trigger_info, Trigger2GB
from pypixxlib.datapixx import DATAPixx3



######### Set directories## ####################################################
cwd_ = os.getcwd()
datawd = os.path.join(cwd_, 'data')
################################################################################

# ==================== SET PARTICIPANT ID ==================== #
date_str = datetime.now().strftime("%Y-%m-%d")

parser = argparse.ArgumentParser()

parser.add_argument("--participant", type=str, required=True)
parser.add_argument("--block", type=int, required=False)

args = parser.parse_args()

participant_id = args.participant


print("Running participant:", participant_id)   

participant_dir = os.path.join(datawd, participant_id)

if not os.path.exists(participant_dir):
    os.makedirs(participant_dir)
    
trials_path = os.path.join(participant_dir, f"{participant_id}_trials.csv")

if not os.path.exists(trials_path):
        shuffle_blocks(participant_id, datawd)

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
TestingPort = True      # True if on a laptop. 

if TestingPort:
    viewing_distance_cm = 57.3    
    monitor_width_cm    = 52.7
    monitor_size_pix    = [1280,720]
    monitor_name        = "testMonitor"
    screen_num = 0  # Change this to the appropriate screen number for the testing setup
    
else:   #----------------------> # change OPM/EEG lab port settings
    viewing_distance_cm = 90    
    monitor_width_cm    = 53.7
    monitor_size_pix    = [1920, 1080]
    monitor_name        = "OPM-lab"
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

# ==================== IMPORT STIMULI ==================== #
stimuli = preload_stimuli(win, stimwd, participant_dir) # for modifying relevant stimuli, see utils_stimuli

rt_clock = core.Clock()
# rt_clock2 = core.Clock()
# onsettime = rt_clock2.getTime()
presenter = StimulusPresenter(window=win, exptimer=rt_clock, triggers=True)

# ==================== EXPORT LOG FILE ==================== #
# Create file path for CSV log
datafile_path = os.path.join(participant_dir, f"{participant_id}_behaviour_{date_str}.csv")

# Open and write headers if file doesn't exist
if not os.path.exists(datafile_path):
    with open(datafile_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['block', 'trial', 'trialtype', 'trialtype_string', 'cuetype', 'cuetype_string', 'correct_key', 'key_pressed','is_resp_corr', 'reaction_time', 'reaction_time_vpixx'])

# ==================== EXPERIMENT ==================== #
if args.block:
    block = args.block
    print("Running block:", block)

else:
    block = range(1, 11)

for BLOCK in block: 
    print(f"Starting Block {BLOCK}...")
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
        
        if BLOCK == 1 and group_idx == 0:

            stimuli['welcome_text'].draw()
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
        drawPixelModeTrigger(win, Trigger2GB(10)) 
        win.flip()
        core.wait(0.5)
        print_trigger_info(device)  # Debugging output to check the video line value
        
        # Show fixation for 2500ms
        stimuli['Fix_Dot'].draw()
        win.flip()
        core.wait(2.5)
    
        # Show cue_cong or cue_incg for 500ms
        cue_stimulus = presenter.get_cue_stimulus(stimuli, cueid)
        cue_trigger_code = presenter.get_cue_trigger_code(cueid)
        presenter.present_cue(cue_stimulus, trigger_code=cue_trigger_code)
        
        print_trigger_info(device) # Debugging output to check the video line value

        # Show fixation. Jitter between 1400-1600ms
        jitter = np.random.choice(np.arange(1.4, 1.61, 0.01))
        jitter = round(jitter, 2)
    
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
            
            arrow_stimulus.draw()
            # Send trigger at Flip
            if target_trigger_code is not None:
                drawPixelModeTrigger(win, Trigger2GB(target_trigger_code))  # send trigger using pixel mode

            timer = core.Clock()
            flip_marks = {}
            device.updateRegisterCache()
            win.callOnFlip(lambda: flip_marks.setdefault('t0_dev', device.getTime()))
            win.callOnFlip(timer.reset)
            win.flip()
            print_trigger_info(device) # Debugging output to check the video line value and timing of trigger relative to stimulus onset
            
            
            # Initialize response variables
            t_0_v = flip_marks['t0_dev']
            button_name = None
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
                    print(f"Button pressed: {key_pressed}")  # Debugging output for button presses and timestamps
                    reaction_time = timer.getTime()
                    reaction_time_vpixx = timestamp - t_0_v  # Calculate reaction time based on VPixx timestamp

                    response_trigger_code = presenter.get_response_trigger_code(key_pressed)
                    presenter.send_trigger_opm(response_trigger_code)  # send response trigger using pixel mode
                    presenter.win.flip()  # Ensure the trigger is sent immediately
                    print_trigger_info(device)  # Debugging output to check the video line value and timing of response trigger
                    # if key_pressed == "white":  # exit button can be reomeved if not desired to allow exit 
                    #     cleanup_and_exit(device, win)
                    # break
                    
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
                        print("pressed during fixation")  # Debugging output to indicate response during fixation
                        print(f"Button pressed: {key_pressed}")  # Debugging output for button presses and timestamps
                        # RT during fixation = 0.5 + time into fixation
                        reaction_time = arrow_duration + timer.getTime()
                        reaction_time_vpixx = timestamp - t_0_v  # Calculate reaction time based on VPixx timestamp
                        response_trigger_code = presenter.get_response_trigger_code(key_pressed)
                        presenter.send_trigger_opm(response_trigger_code)
                        presenter.win.flip() 
                        print_trigger_info(device)  # Ensure the trigger is sent immediately

                        # if key_pressed == 'white':  # exit button can be reomeved if not desired to allow exit 
                        #     cleanup_and_exit(device, win)
                        # break

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
            
            reaction_time = round(reaction_time, 4) if reaction_time is not None else None
            reaction_time_vpixx = round(reaction_time_vpixx, 4) if reaction_time_vpixx is not None else None
            # Write to CSV
            print(f"key_pressed: {key_pressed}")
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
                    reaction_time_vpixx, # reaction time based on VPixx timestamp
                ])

    # Calculate and display accuracy
    if total_trials > 0:
        accuracy_percentage = (correct_responses / total_trials) * 100
    else:
        accuracy_percentage = 0

    # Create accuracy feedback text
    accuracy_text = visual.TextStim(
        win,
        text=f'Block {BLOCK}/10 is now complete. \n\nYou were correct on {accuracy_percentage:.1f}% of trials.\n\nThank you for your participation! \n\n We will now take a short break before the next block begins.',
        color='white',
        height=1,
        pos=(0, 0),
        units='deg',
        wrapWidth=60
    )
    accuracy_text_DE = visual.TextStim(
        win,
        text=f'Block {BLOCK}/10 ist jetzt abgeschlossen. \n\nSie waren auf {accuracy_percentage:.1f}% der Versuche korrekt.\n\nVielen Dank für Ihre Teilnahme! \n\n Wir werden jetzt eine kurze Pause einlegen, bevor der nächste Block beginnt.',
        color='white',
        height=1,
        pos=(0, 0),
        units='deg',
        wrapWidth=60
    )

    accuracy_text = accuracy_text_DE  # Assuming you want to show the German version of the accuracy text

    accuracy_text.draw()
    win.flip()
    # wait until spacebar on keyboard is pressed to move to next block
    event.clearEvents()
    while True:
        keys = event.getKeys(keyList=['space', 'escape'])
        if 'space' in keys:
            print(f"Starting next block: {BLOCK + 1}")
            break
        elif 'escape' in keys:
            cleanup_and_exit(device, win)
    core.wait(1)