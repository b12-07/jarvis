import speech_recognition as sr
import audioop
import numpy as np

class SpeechToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()

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
                text = self.recognizer.recognize_google(audio)
                return text
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return ""
        except Exception as e:
            print(f"STT Error: {e}")
            return ""
