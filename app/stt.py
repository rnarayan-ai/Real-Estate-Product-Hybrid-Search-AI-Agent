# app/stt.py
import os
import re
import io
import speech_recognition as sr
from autocorrect import Speller
from app.nlu import NLUProcessor

class SpeechToText:
    """
    Handles Speech-to-Text (STT) conversion for voice-based queries.
    Supports:
      - Google SpeechRecognition API (default)
      - Offline VOSK model (if installed and configured)
    """

    def __init__(self):
        self.mode = os.getenv("STT_MODE", "google")  # or "vosk"
        self.recognizer = sr.Recognizer()
        self.vosk_model = None
        self.corrector = Speller(lang="en")
        self.nlu = NLUProcessor()

        if self.mode == "vosk":
            try:
                from vosk import Model
                vosk_path = os.getenv("VOSK_MODEL_PATH", "vosk-model-small-en-us-0.15")
                self.vosk_model = Model(vosk_path)
                print(f"[STT] Loaded VOSK model from {vosk_path}")
            except Exception as e:
                print(f"[STT] Warning: VOSK model not found or not installed: {e}")
                self.mode = "google"  # fallback

    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribes an audio file (WAV/FLAC/MP3).
        """
        try:
            with sr.AudioFile(audio_path) as source:
                audio_data = self.recognizer.record(source)

                if self.mode == "google":
                    text = self.recognizer.recognize_google(audio_data)
                elif self.mode == "vosk" and self.vosk_model:
                    from vosk import KaldiRecognizer
                    import json
                    rec = KaldiRecognizer(self.vosk_model, 16000)
                    rec.AcceptWaveform(audio_data.get_raw_data())
                    text = json.loads(rec.Result()).get("text", "")
                else:
                    raise Exception("No valid STT mode configured")

                print(f"[STT] Transcribed text: {text}")
                return text

        except Exception as e:
            print(f"[STT] Error: {e}")
            return ""

    def transcribe_microphone(self) -> str:
        """
        Captures speech directly from microphone input (for live queries).
        """
        try:
            with sr.Microphone() as source:
                print("[STT] Speak now...")
                audio_data = self.recognizer.listen(source)
                text = self.recognizer.recognize_google(audio_data)
                print(f"[STT] Transcribed text: {text}")
                return text
        except Exception as e:
            print(f"[STT] Error from mic: {e}")
            return ""

    def convert(self, audio_file: bytes) -> str:
        """
        Converts speech from an audio file (.wav, .mp3, etc.) into text.
        Returns normalized text string.
        """
        try:
            with sr.AudioFile(io.BytesIO(audio_file)) as source:
                audio_data = self.recognizer.record(source)

            if self.mode == "google":
                text = self.recognizer.recognize_google(audio_data)
            elif self.mode == "sphinx":
                text = self.recognizer.recognize_sphinx(audio_data)
            elif self.mode == "vosk":
                # Optional: VOSK backend if installed separately
                import vosk
                model_path = os.getenv("VOSK_MODEL", "vosk-model-small-en-us-0.15")
                if not os.path.exists(model_path):
                    raise FileNotFoundError(f"VOSK model not found: {model_path}")
                model = vosk.Model(model_path)
                rec = vosk.KaldiRecognizer(model, 16000)
                rec.AcceptWaveform(audio_data.get_raw_data())
                text = rec.Result()
            else:
                text = self.recognizer.recognize_google(audio_data)

            # Clean, autocorrect and normalize
            text = self.nlu.normalize(text)
            return text

        except sr.UnknownValueError:
            return "Sorry, I could not understand the audio clearly."
        except sr.RequestError as e:
            return f"Speech recognition service error: {e}"
        except Exception as e:
            print(f"[STT] Error: {e}")
            return "Error during speech-to-text conversion."

    def normalize_text(self, text: str) -> str:
        """
        Applies basic text normalization:
        - Lowercasing
        - Removing unwanted characters
        - Spell correction
        """
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", "", text)
        corrected = " ".join(self.corrector(word) for word in text.split())
        return corrected.strip()

# Example usage
if __name__ == "__main__":
    stt = SpeechToText()
    # Example: Convert voice query
    # text = stt.transcribe_audio("samples/query.wav")
    text = stt.transcribe_microphone()
    print("User said:", text)
