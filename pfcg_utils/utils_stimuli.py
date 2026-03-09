from psychopy import visual, core, event, monitors, logging, sound, parallel
import psychtoolbox as ptb
import numpy as np

# Initialize port (use your correct address)
TestingPort = True # True if on a laptop. False if in EEG-lab/Sudring -----------> ADAPT


if TestingPort:
    port = None
else:
    from psychopy import parallel
    try:
        port = parallel.ParallelPort(address=0x378)
    except Exception:
        print("Parallel port not found, setting to None")
        port = None



# Send trigger function
#def send_trigger(code, timer=None):
#    """
#    Sends a trigger code with a pulse duration in seconds.
#    """
#    pulse_duration=0.01
#    port.setData(code)
#    if timer:
#        print(round(timer.getTime(), 3))
#    core.wait(pulse_duration)  # hold trigger
#    port.setData(0)            # clear trigger
#    #core.wait(pulse_duration)  # wait before next trigger

# Seconds to frames
def sec_to_fr(dur_s, rrate):
    return int(np.fix(dur_s * rrate))


# Class to present stimuli
class StimulusPresenter:
    def __init__(self, window, exptimer, triggers=True):
        self.win        = window
        self.timer      = None         
        self.triggers   = triggers
        self.blcode     = 2
        self.nstim      = 4
        
        # FIXED: Only try to open the port if we are NOT on the laptop (TestingPort = False)
        if self.triggers and not TestingPort:
            try:
                self.port = parallel.ParallelPort(address=0x378)
            except Exception:
                print("Parallel port failed to open. Setting self.port to None.")
                self.port = None
        else:
            self.port = None

    def send_trigger(self, code, pulse_duration=0.01):
        """Sends a trigger code with a pulse duration in seconds."""
        if self.triggers and self.port is not None:
            self.port.setData(code)
            core.wait(pulse_duration)
            self.port.setData(0)
            core.wait(pulse_duration)

    def present_stimulus(self, stimulus, duration, trigger_code=None):
        """Present a single stimulus for a specified duration"""
        
        stimulus.draw()
        self.win.flip()
        if trigger_code is not None:
            self.send_trigger(trigger_code)
        core.wait(duration)

    def present_RS(self, resting_state, duration=60, trigger_code=7):
        """Present fixation dot for resting state measurement"""
        self.present_stimulus(resting_state, duration, trigger_code)

    def present_fixation(self, fixation, duration=None, trigger_code=9):
        """Present fixation dot for specified duration"""
        self.present_stimulus(fixation, duration, trigger_code)
        return duration

    def present_cue(self, cue_stimulus, duration=0.5, trigger_code=None):
        """Present congruent or incongruent cue"""
        self.present_stimulus(cue_stimulus, duration, trigger_code)

    def target_type(self, stimuli, trialid):
        """Get the appropriate arrow stimulus based on trial type"""
        if trialid in [0, 2]:  # right grating trials
            return stimuli['right_grating'][0]
        elif trialid in [1, 3]:  # left grating trials
            return stimuli['left_grating'][0]
        else:
            raise ValueError(f"Unknown trialtype: {trialid}")

    def target_response(self, arrow_stimulus, fixation_stimulus, arrow_duration=0.5, response_window=2.0, trigger_code=None):
        """Present arrow stimulus and show fixation while monitoring for responses"""
        if trigger_code is not None:
            self.send_trigger(trigger_code)
        
        # Show arrow stimulus
        arrow_stimulus.draw()
        self.win.flip()
        
        # Start timer at target onset
        timer = core.Clock()
        core.wait(arrow_duration)
        
        # Show fixation for remaining response window
        fixation_stimulus.draw()
        self.win.flip()
        
        return timer

    def get_cue_stimulus(self, stimuli, cueid):
        """Get the appropriate cue stimulus based on cue type"""
        if cueid == 1:
            return stimuli['cue_cong']
        else:
            return stimuli['cue_incg']

    def get_cue_trigger_code(self, cueid):
        """Get trigger code for cue based on cue type"""
        if cueid == 1:
            return 200  # cong cue
        else:
            return 100  # incg cue

    def get_target_trigger_code(self, trialid, trial_position):
        """Get trigger code for target stimulus based on trial type and position in sequence
        
        Args:
            trialid: Trial type (0=right_cong, 1=left_cong, 2=right_incg, 3=left_incg)
            trial_position: Position of trial within the 5-trial sequence (1-5)
        """
        base_codes = {
            0: 135,  # right_cong: 135-145-155-165-175
            1: 130,  # left_cong:  130-140-150-160-170
            2: 35,   # right_incg: 35-45-55-65-75
            3: 30    # left_incg:  30-40-50-60-70
        }
        
        return base_codes[trialid] + (trial_position - 1) * 10
    

    def get_response_trigger_code(self, key_pressed):
        if key_pressed == 65531:
            return 3
        elif key_pressed == 65534: 
            return 4
        else: 
            return 5