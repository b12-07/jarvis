import asyncio
import edge_tts
import pygame
import os
import tempfile

class TextToSpeech:
    def __init__(self):
        # Initialize pygame mixer for audio playback, handle headless environments
        try:
            pygame.mixer.init()
            self.mixer_initialized = True
        except pygame.error as e:
            print(f"Failed to initialize pygame mixer (likely headless): {e}")
            self.mixer_initialized = False

        self.voice = "en-GB-RyanNeural"  # Good voice for a British AI (Tony Stark style)

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

            if self.mixer_initialized:
                # Play the audio
                pygame.mixer.music.load(output_file)
                pygame.mixer.music.play()

                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

                # Cleanup
                pygame.mixer.music.unload()
            else:
                print(f"[TTS Audio output suppressed, running headless]: {text}")

            if os.path.exists(output_file):
                os.remove(output_file)

        except Exception as e:
            print(f"TTS Error: {e}")
