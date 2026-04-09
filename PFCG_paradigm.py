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
from pfcg_utils.PixelMode import drawPixelModeTrigger, print_trigger_info, Trigger2GB, sec_to_fr
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
parser.add_argument("--viewing_distance", type=float, required=False)

args = parser.parse_args()

participant_id = args.participant
if args.viewing_distance:
    viewing_distance_cm = args.viewing_distance

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
Testing = True      # True if on a laptop. 

if Testing:   #----------------------> # change to laptop 
    viewing_distance_cm = 57.3   
    monitor_width_cm    = 52.7
    monitor_size_pix    = [1280,720]
    monitor_name        = "testMonitor"
    monitor_rr = 60
    screen_num = 0  # Change this to the appropriate screen number for the testing setup
    
else:   #----------------------> # change OPM/EEG lab port settings
    viewing_distance_cm = viewing_distance_cm if args.viewing_distance else 90
    monitor_width_cm    = 53.7
    monitor_size_pix    = [1920, 1080]
    monitor_name        = "OPM-lab"
    monitor_rr = 120
    screen_num = 2  # Change this to the appropriate screen number for the OPM lab setup
    

trigger_duration = 2/monitor_rr  # Duration of trigger pulse in seconds

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
presenter = StimulusPresenter(window=win, triggers=True, trigger_duration=trigger_duration)  # Initialize the StimulusPresenter with trigger duration

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

    # Display instruction to be steady
    instruction_text = visual.TextStim(
        win,
        text="Entspannen Sie sich und bewegen Sie sich während der Aufgabe nicht.",
        color='white',
        height=1,
        pos=(0, 0),
        units='deg',
        wrapWidth=60
    )
    instruction_text.draw()
    win.flip()
    while True:
        keys = event.getKeys(keyList=['space', 'escape'])
        if 'space' in keys:
            break
        elif 'escape' in keys:
            cleanup_and_exit(device, win)
    
    if BLOCK != 1:
        # Countdown with number in circle like a movie
            for i in range(3, 0, -1):
                circle = visual.Circle(win, radius=10, fillColor='white', lineColor='white', units='deg')
                circle.draw()
                countdown_text = visual.TextStim(win, text=str(i), color='black', height=5.5, pos=(0, 0), units='deg', bold=True)
                countdown_text.draw()
                win.flip()
                core.wait(1)
            
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

            for i in range(3, 0, -1):
                circle = visual.Circle(win, radius=10, fillColor='white', lineColor='white', units='deg')
                circle.draw()
                countdown_text = visual.TextStim(win, text=str(i), color='black', height=5.5, pos=(0, 0), units='deg', bold=True)
                countdown_text.draw()
                win.flip()
                core.wait(1)
        
        # Task begins here for each mini-block
        stimuli['cue_baseline'].draw()
        drawPixelModeTrigger(win, Trigger2GB(10)) 
        win.flip()
        core.wait(trigger_duration)  # Adjusted to account for time taken by two flips and drawing the cue again
        print_trigger_info(device) 
        stimuli['cue_baseline'].draw()
        win.flip()
        core.wait(0.5 - trigger_duration)  # Adjusted to account for time taken by two flips and drawing the cue again

        # Show fixation for 2500m
        stimuli['Fix_Dot'].draw()
        win.flip()
        core.wait(2.5)
    
        # Show cue_cong or cue_incg for 500ms
        cue_stimulus = presenter.get_cue_stimulus(stimuli, cueid)
        cue_trigger_code = presenter.get_cue_trigger_code(cueid)
        presenter.present_cue(cue_stimulus, trigger_code=cue_trigger_code, device=device)  # This function now handles both the trigger and the timing of the cue presentation

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
            
            timer = core.Clock()
            flip_marks = {}
            device.updateRegisterCache()
            win.callOnFlip(lambda: flip_marks.setdefault('t0_dev', device.getTime()))
            win.callOnFlip(timer.reset)
             # Initialize response variables
           
            button_name = None
            key_pressed = None
            reaction_time = None
            reaction_time_vpixx = None
            arrow_duration = 0.5
            # response_deadline = arrow_duration + jitter
            key_press_frame = None

            for frames in range(sec_to_fr(arrow_duration, monitor_rr)):  # Show target for 0.5s

                button_name, timestamp = read_button_press(device, myLog)  # Check for button presses
               

                # Send trigger at Flip
                if frames < 2:  # Only send trigger for two frame and if no response yet
                    arrow_stimulus.draw()
                    drawPixelModeTrigger(win, Trigger2GB(target_trigger_code))
                    win.flip()
                    t_0_v = flip_marks['t0_dev']  # send trigger using pixel mode                   
                    print_trigger_info(device) # Debugging output to check the video line value and timing of trigger relative to stimulus onset
                
                elif button_name is not None: 

                    key_pressed = button_name
                    key_press_frame = frames

                    reaction_time = timer.getTime()
                    reaction_time_vpixx = timestamp - t_0_v  # Calculate reaction time based on VPixx timestamp

                    response_trigger_code = presenter.get_response_trigger_code(key_pressed)
                    
                    arrow_stimulus.draw()
                    presenter.send_trigger_opm(response_trigger_code)  # send response trigger using pixel mode
                    presenter.win.flip() 
                    # core.wait(trigger_duration)  # Ensure the trigger is sent immediately
                    # print_trigger_info(device)  # Debugging output to check the video line value and timing of response trigger
                    flush_button_buffer(device, myLog)  # Clear any old button presses from the buffer
                elif key_press_frame:
                    arrow_stimulus.draw()
                    presenter.send_trigger_opm(response_trigger_code)  # send response trigger using pixel mode
                    presenter.win.flip() # Response already given during target, just wait the full jitter duration
                    print_trigger_info(device)  # Debugging output to check the video line value and timing of response trigger
                    key_press_frame = None
                else:
                    arrow_stimulus.draw()
                    # if frames == sec_to_fr(arrow_duration, monitor_rr) - 1:  # On the last frame of the target presentation, print the timing information
                        # win.callOnFlip(lambda: print(timer.getTime(), "seconds since target onset (should be close to 0.5s)"))  # Debugging output to check timing of target presentation
                    win.flip()
                    
                
            # Show fixation
            stimuli['Fix_Dot'].draw()
            win.callOnFlip(timer.reset)  # Mark fixation onset time
            win.flip()

            # Continue monitoring during fixation if no response yet
            if button_name is None:
                for frames in range(sec_to_fr(jitter, monitor_rr)-1):
                    # flush_button_buffer(device, myLog)  # Clear any old button presses from the buffer
                    button_name, timestamp = read_button_press(device, myLog)  # Check for button presses
                    if button_name is not None:
                        key_pressed = button_name
                        key_press_frame = frames
                        # print("pressed during fixation")  # Debugging output to indicate response during fixation
                        # print(f"Button pressed: {key_pressed}")  # Debugging output for button presses and timestamps
                        # RT during fixation = 0.5 + time into fixation
                        reaction_time = arrow_duration + timer.getTime()
                        reaction_time_vpixx = timestamp - t_0_v  # Calculate reaction time based on VPixx timestamp
                        
                        response_trigger_code = presenter.get_response_trigger_code(key_pressed)

                        stimuli['Fix_Dot'].draw()
                        presenter.send_trigger_opm(response_trigger_code)
                        presenter.win.flip() 

                        # print_trigger_info(device)  # Ensure the trigger is sent immediately
                    elif key_press_frame:
                        stimuli['Fix_Dot'].draw()
                        presenter.send_trigger_opm(response_trigger_code)  # send response trigger using pixel mode
                        presenter.win.flip() # Response already given during target, just wait the full jitter duration
                        print_trigger_info(device)  
                        key_press_frame = None  # Debugging output to check the video line value and timing of response trigger
                    else:
                        stimuli['Fix_Dot'].draw()
                        win.flip()

                # Wait for any remaining fixation time
                # remaining_time = jitter - timer.getTime()
                # if remaining_time > 0:
                #     core.wait(remaining_time)
                    
            else:
                for frames in range(sec_to_fr(jitter, monitor_rr)-1):
                    stimuli['Fix_Dot'].draw()
                    win.flip()
                
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
            # print(f"key_pressed: {key_pressed}")
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
        text=f'Block {BLOCK}/10 ist jetzt abgeschlossen. \n\nIhre Antworten waren zu {accuracy_percentage:.1f}% richtig.\n\nVielen Dank für Ihre Teilnahme! \n\n Wir werden jetzt eine kurze Pause einlegen, bevor der nächste Block beginnt.',
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