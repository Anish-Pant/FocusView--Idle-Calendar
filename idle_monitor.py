import ctypes
import ctypes.wintypes

# Define the LASTINPUTINFO structure from the Windows API. Thisstructure is used to retrieve the time of the last input event.
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]

def get_idle_time():
 #Returns the number of seconds the system has been idle (Windows only). It works by comparing the tick count of the last input event with the current system tick count.
    
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = ctypes.sizeof(lastInputInfo)

    # Call the GetLastInputInfo function from user32.dll. [9]
    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo)):
        # Get the current system tick count.
        current_tick = ctypes.windll.kernel32.GetTickCount()
        last_input_tick = lastInputInfo.dwTime
        
        # Calculate the idle time in milliseconds.
        idle_millis = current_tick - last_input_tick
        
        # Return idle time in seconds.
        return idle_millis / 1000.0
        
    return 0.0 # Return 0.0 on failure.