import speech_recognition as sr
import numpy as np
import socket
import urllib.error

class SpeechToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def transcribe_audio(self, sr_audio, language="tr-TR") -> str:
        """Safely transcribes audio, catching all socket and network errors."""
        try:
            return self.recognizer.recognize_google(sr_audio, language=language)
        except sr.UnknownValueError:
            print("[STT] Google Speech Recognition could not understand audio.")
            return ""
        except sr.RequestError as e:
            print(f"[STT] API request failed (Service unavailable/Network error): {e}")
            return ""
        except (OSError, socket.error, urllib.error.URLError) as e:
            print(f"[STT] Network connection failed: {e}")
            return ""
        except Exception as e:
            print(f"[STT] Unexpected error during transcription: {e}")
            return ""

    def listen_and_transcribe(self, mic_index=None, amplitude_callback=None):
        """
        Listens to the microphone and transcribes speech to text.
        If amplitude_callback is provided, it can be called periodically with the audio amplitude.
        However, speech_recognition's standard listen() blocks.
        For true live amplitude, we can hook into the audio stream or do a background listen.
        For simplicity, we'll use a custom record loop if a callback is provided.
        """
        try:
            with sr.Microphone(device_index=mic_index) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Listening...")

                # If we need live amplitude during recording, we can chunk it
                # For this implementation, we'll just record and transcribe
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)

                print("Processing speech...")
                return self.transcribe_audio(audio, language="tr-TR")
        except sr.WaitTimeoutError:
            return ""
        except Exception as e:
            print(f"[STT] Microphone Error: {e}")
            return ""
