import threading
import time
import sys
import os

print(f"DEBUG: Python Executable: {sys.executable}")
print(f"DEBUG: Python Version: {sys.version}")

try:
    import speech_recognition as sr
    import pyttsx3
except ImportError as e:
    sr = None
    pyttsx3 = None
    print(f"XeNit Voice: Dependencies missing. Specific Error: {e}")

class VoiceManager:
    def __init__(self):
        self.enabled = (sr is not None and pyttsx3 is not None)
        self.is_listening = False
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        
        if self.enabled:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                self.tts_engine = pyttsx3.init()
                
                # Configure TTS Voice (Try to find a good one)
                voices = self.tts_engine.getProperty('voices')
                for voice in voices:
                    if "zira" in voice.name.lower(): # Windows specific good female voice
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                        
                self.tts_engine.setProperty('rate', 170) # Slightly faster
            except Exception as e:
                print(f"XeNit Voice Init Error: {e}")
                self.enabled = False

    def speak(self, text):
        if not self.enabled or not text: return
        
        def _speak_thread():
            try:
                # Clean text of markdown
                clean_text = text.replace("**", "").replace("__", "").replace("`", "")
                self.tts_engine.say(clean_text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"XeNit TTS Error: {e}")
                
        threading.Thread(target=_speak_thread, daemon=True).start()

    def listen_once(self, callback_success, callback_error=None):
        """
        Listens for a single command in a background thread.
        callback_success(text): Called with transcribed text.
        callback_error(msg): Called with error message.
        """
        if not self.enabled:
            if callback_error: callback_error("Voice module disabled.")
            return

        def _listen_thread():
            self.is_listening = True
            try:
                with self.microphone as source:
                    print("XeNit Voice: Adjusting for ambient noise...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    print("XeNit Voice: Listening...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    
                print("XeNit Voice: Processing...")
                text = self.recognizer.recognize_google(audio)
                print(f"XeNit Voice Recognized: {text}")
                
                if callback_success:
                    callback_success(text)
                    
            except sr.WaitTimeoutError:
                if callback_error: callback_error("No speech detected.")
            except sr.UnknownValueError:
                if callback_error: callback_error("Could not understand audio.")
            except sr.RequestError:
                if callback_error: callback_error("Speech service unavailable.")
            except Exception as e:
                if callback_error: callback_error(f"Error: {str(e)}")
            finally:
                self.is_listening = False
                
        threading.Thread(target=_listen_thread, daemon=True).start()
