import speech_recognition as sr

def transcribe_audio_google(audio_path: str, language: str = "fa-IR") -> str:
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio_data, language=language)
    except sr.UnknownValueError:
        raise ValueError("Could not understand audio")
    except sr.RequestError as e:
        raise ValueError(f"Could not request results from Google Speech Recognition service; {e}")