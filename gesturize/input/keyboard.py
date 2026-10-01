
import os
import subprocess
 
# open and close require admin priveleges on Windows
# current keyboard implmentation only works on Windows
class KeyboardController:
    def __init__(self):
        self.open = False
 
    def toggle(self):
        if self.open:
            self._close()
        else:
            self._open()

    def _open(self):
        os.startfile("osk.exe")
        self.open = True
 
    def _close(self):
        result = subprocess.run(["taskkill", "/IM", "osk.exe", "/F"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Could not close On-Screen Keyboard: {result.stderr.strip()}")
            print("If this says 'Access is denied', try running main.py as Administrator.")
        self.open = False