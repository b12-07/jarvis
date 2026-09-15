import sys
import threading
import queue
import time
import speech_recognition as sr

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, QThread

from ui.main_window import MainWindow
from brain.llm import JarvisBrain
from speech.stt import SpeechToText
from speech.tts import TextToSpeech

class AudioWorker(QThread):
    amplitude_update = Signal(float)
    transcription_complete = Signal(str)

    def __init__(self, stt_module: SpeechToText):
        super().__init__()
        self.stt = stt_module
        self.is_listening = False
        self.audio_queue = queue.Queue()

    def run(self):
        # We start a custom PyAudio stream to get live amplitude AND transcribe
        import pyaudio
        import numpy as np

        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000

        p = pyaudio.PyAudio()
        try:
            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
        except Exception as e:
            print(f"Could not open audio stream: {e}")
            self.transcription_complete.emit("")
            return

        frames = []
        print("Audio stream opened, capturing...")

        while self.is_listening:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)

                # Calculate amplitude
                audio_data = np.frombuffer(data, dtype=np.int16)
                if len(audio_data) > 0:
                    amplitude = np.abs(audio_data).mean() / 32768.0  # Normalize to 0-1
                    # Amplify visual effect
                    amplitude = min(amplitude * 10, 1.0)
                    self.amplitude_update.emit(float(amplitude))

            except Exception as e:
                print(f"Error reading stream: {e}")
                break

        print("Stopping audio stream...")
        stream.stop_stream()
        stream.close()
        p.terminate()

        if not frames:
            self.transcription_complete.emit("")
            return

        # Convert raw frames to AudioData for SpeechRecognition
        import speech_recognition as sr
        audio_data = b''.join(frames)
        sr_audio = sr.AudioData(audio_data, RATE, 2) # sample_rate=16000, sample_width=2

        print("Transcribing...")
        try:
            text = self.stt.recognizer.recognize_google(sr_audio)
            print(f"Transcribed: {text}")
            self.transcription_complete.emit(text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            self.transcription_complete.emit("")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            self.transcription_complete.emit("")
        except Exception as e:
            print(f"STT Error: {e}")
            self.transcription_complete.emit("")

class JarvisController(QObject):
    def __init__(self):
        super().__init__()

        # Initialize Core Modules
        self.brain = JarvisBrain()
        self.stt = SpeechToText()
        self.tts = TextToSpeech()

        # Initialize UI
        self.app = QApplication(sys.argv)
        self.window = MainWindow()

        # Wire UI signals
        self.window.push_to_talk_started.connect(self.start_listening)
        self.window.push_to_talk_ended.connect(self.stop_listening)

        # Worker threads
        self.audio_worker = None
        self.speech_thread = None

    def start_listening(self):
        # Stop any ongoing speech
        import pygame
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except:
            pass

        self.audio_worker = AudioWorker(self.stt)
        self.audio_worker.is_listening = True
        self.audio_worker.amplitude_update.connect(self.window.visualizer.set_amplitude)
        self.audio_worker.transcription_complete.connect(self.handle_transcription)
        self.audio_worker.start()

    def stop_listening(self):
        if self.audio_worker:
            self.audio_worker.is_listening = False
            # Wait for transcription...

    def handle_transcription(self, text: str):
        if not text:
            self.window.set_status("Idle")
            return

        self.window.set_status("Thinking...")

        # Process in brain (blocking, could be threaded, but keeps flow simple for now)
        threading.Thread(target=self._process_and_speak, args=(text,), daemon=True).start()

    def _process_and_speak(self, text: str):
        response = self.brain.process_input(text)
        print(f"Jarvis: {response}")

        # Update UI safely (should technically use signals for Qt thread safety, but simple string update often works)
        # We will use QMetaObject.invokeMethod to be thread-safe
        from PySide6.QtCore import QMetaObject, Qt, Q_ARG
        QMetaObject.invokeMethod(self.window, "set_status", Qt.QueuedConnection, Q_ARG(str, "Speaking"))

        self.tts.speak(response)

        QMetaObject.invokeMethod(self.window, "set_status", Qt.QueuedConnection, Q_ARG(str, "Idle"))

    def run(self):
        self.window.show()

        # Welcome message
        threading.Thread(target=self._initial_greeting, daemon=True).start()

        return self.app.exec()

    def _initial_greeting(self):
        time.sleep(1)
        from PySide6.QtCore import QMetaObject, Qt, Q_ARG
        QMetaObject.invokeMethod(self.window, "set_status", Qt.QueuedConnection, Q_ARG(str, "Speaking"))
        self.tts.speak("Systems online, sir. Jarvis is ready.")
        QMetaObject.invokeMethod(self.window, "set_status", Qt.QueuedConnection, Q_ARG(str, "Idle"))

if __name__ == "__main__":
    controller = JarvisController()
    sys.exit(controller.run())
