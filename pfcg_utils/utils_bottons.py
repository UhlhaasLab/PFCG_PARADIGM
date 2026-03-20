from psychopy import visual, core, event
from pypixxlib import _libdpx as dp

from pfcg_utils.PixelMode import RGB2Trigger

BUTTON_CODES_ALL = {65527:'blue', 65533:'yellow', 65534:'red', 65531:'green', 65519:'white', 65535:'button release'}
# 
#BUTTON_CODES_ALL = { 65528: 'blue', 65522: 'yellow', 65521: 'red', 65524: 'green', 65520: 'button release' }

def stopButtons(startAndStopButtons):
    while True:
        dp.DPxUpdateRegCache()
        state = dp.DPxGetDinValue()
        # print(f"Current button state: {state}")
        
        if state  in startAndStopButtons:
            return state


def read_button_press(device, button_log):
    """
    Read button presses from VPixx device.
    
    Returns:
        tuple: (button_name, timestamp) or (None, None) if no button pressed
    """
    if device is None:
        return None, None
    
    try:
        device.updateRegisterCache()
        device.din.getDinLogStatus(button_log)
        new_events = button_log["newLogFrames"]
        
        if new_events > 0:
            event_list = device.din.readDinLog(button_log, new_events)
            for timestamp, code in event_list:
                if code in BUTTON_CODES_ALL:
                    button_name = BUTTON_CODES_ALL[code]
                    # # Only return green or red button presses
                    if button_name in ("red", "green","white"):
                        return button_name, timestamp
    except Exception as e:
        print(f"✗ Error reading button: {e}")
    
    return None, None


def flush_button_buffer(device, button_log):
    """Clear all pending button events from the buffer."""
    if device is None:
        return
    
    try:
        while True:
            # dp.DPxUpdateRegCache()
            device.updateRegisterCache()
            device.din.getDinLogStatus(button_log)
            n = button_log.get("newLogFrames", 0)
            
            if not n:
                break
            device.din.readDinLog(button_log, n)
            
        # print("✓ Button buffer flushed")
    except Exception as e:
        print(f"✗ Error flushing button buffer: {e}")


def cleanup_and_exit(device, win):
    """Proper cleanup before exiting."""
    try:
        if device:
            device.close()
        if win:
            win.close()
        core.quit()
    except Exception as e:
        print(f"✗ Error during cleanup: {e}")
        core.quit()

