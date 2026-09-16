import asyncio
import edge_tts
import os
import sys
import tempfile
import subprocess

class TextToSpeech:
    def __init__(self):
        self.voice = "tr-TR-AhmetNeural"  # Turkish voice for Jarvis

    async def _generate_audio(self, text: str, output_file: str):
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_file)

    def speak(self, text: str):
        if not text:
            return

        try:
            # Generate a temporary file to store the audio
            temp_dir = tempfile.gettempdir()
            output_file = os.path.join(temp_dir, "jarvis_output.mp3")

            # Generate audio using edge-tts (async run in sync context)
            asyncio.run(self._generate_audio(text, output_file))

            # Play the audio based on the platform
            try:
                if sys.platform == "darwin":
                    subprocess.run(["afplay", output_file], check=True)
                elif sys.platform == "win32":
                    os.startfile(output_file)
                    # wait for a bit since os.startfile doesn't block
                    import time
                    time.sleep(3) # Crude fallback for Windows
                elif sys.platform == "linux":
                    # For linux try standard players if they exist, otherwise just print
                    subprocess.run(["mpg123", output_file], check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except Exception as play_error:
                print(f"[TTS Audio playback failed or headless]: {text} - {play_error}")

            if os.path.exists(output_file):
                # Clean up if not on windows (windows might lock the file while playing)
                if sys.platform != "win32":
                    os.remove(output_file)

        except Exception as e:
            print(f"TTS Error: {e}")
