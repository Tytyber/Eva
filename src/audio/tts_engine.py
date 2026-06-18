import pyttsx3 # pip install pyttsx3

class TTSEngine:
    def __init__(self):
        print("🔊 Инициализация синтезатора речи...")
        self.engine = pyttsx3.init()
        # Настройки для русского голоса (если доступен)
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'russian' in voice.name.lower() or 'ru' in voice.id.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        self.engine.setProperty('rate', 180) # Скорость речи
        self.engine.setProperty('volume', 1.0) # Громкость

    def speak(self, text: str):
        """Озвучивает текст."""
        print(f"🗣️ Озвучиваю: {text}")
        self.engine.say(text)
        self.engine.runAndWait()