import speech_recognition as sr
import pyttsx3

class VoiceTool:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()

    def speak(self, text):
        print(f"[AZAD VOICE]: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """مائیک سے آواز سن کر اسے ٹیکسٹ میں بدلے گا"""
        with sr.Microphone() as source:
            print("\n[AZAD] سن رہا ہوں... کچھ بولیں:")
            # شور کو کم کرنے کے لیے
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("[AZAD] پروسیس ہو رہا ہے...")
                text = self.recognizer.recognize_google(audio, language='ur-PK') # اردو یا انگریزی کے لیے
                print(f"آپ نے کہا: {text}")
                return text
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                self.speak("معذرت، میں آپ کی بات سمجھ نہیں سکا۔ دوبارہ کہیے۔")
                return ""
            except Exception as e:
                print(f"وائس ایرر: {e}")
                return ""