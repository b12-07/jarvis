import os
import platform
import subprocess
import psutil
from typing import Dict, Optional, Tuple

class SystemActions:
    def __init__(self, app_aliases: Dict[str, str]):
        self.os_name = platform.system().lower()
        self.app_aliases = app_aliases

    def get_system_metrics(self) -> str:
        """Returns the current CPU and RAM usage percentages."""
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        return f"CPU: {cpu}%, RAM: {ram}%"

    def launch_app(self, app_name: str) -> str:
        """Launches an application by name. Example: 'chrome' or 'spotify'."""
        app_target = self.app_aliases.get(app_name.lower(), app_name)
        try:
            if self.os_name == "darwin":  # macOS
                subprocess.Popen(["open", "-a", app_target])
                return f"Successfully launched {app_target} on macOS."
            elif self.os_name == "windows":
                os.startfile(app_target) if hasattr(os, 'startfile') else subprocess.Popen(["start", app_target], shell=True)
                return f"Successfully launched {app_target} on Windows."
            elif self.os_name == "linux":
                subprocess.Popen([app_target])
                return f"Successfully launched {app_target} on Linux."
            return f"Failed to launch {app_target}. OS unsupported."
        except Exception as e:
            error_msg = f"Failed to launch app {app_name}: {e}"
            print(error_msg)
            return error_msg

    def adjust_volume(self, level: int) -> str:
        """Adjusts system master volume. Level must be an integer between 0 and 100."""
        level = max(0, min(100, level))
        try:
            if self.os_name == "darwin":
                # Convert 0-100 to 0-7 (or 0-100 for some versions of osascript)
                # Actually, set volume output volume X works well
                subprocess.run(["osascript", "-e", f"set volume output volume {level}"], check=True)
                return f"Volume set to {level}% on macOS."
            elif self.os_name == "windows":
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                try:
                    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                except ImportError:
                    print("pycaw is required for precise Windows volume control. Installing via pip is recommended.")
                    subprocess.run(["powershell", "-Command", f"(new-object -com wscript.shell).SendKeys([char]175)"], check=False)
                    return f"Volume control approximated. Pycaw not found."

                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))

                # Convert 0-100 to decibels or scalar
                # Pycaw scalar is 0.0 to 1.0
                scalar_level = level / 100.0
                volume.SetMasterVolumeLevelScalar(scalar_level, None)
                return f"Volume set to {level}% on Windows."
            elif self.os_name == "linux":
                # PulseAudio / ALSA
                subprocess.run(["amixer", "-D", "pulse", "sset", "Master", f"{level}%"], check=True)
                return f"Volume set to {level}% on Linux."
            return "Failed to adjust volume: OS unsupported."
        except Exception as e:
            error_msg = f"Failed to adjust volume: {e}"
            print(error_msg)
            return error_msg
