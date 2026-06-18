from typing import Optional
from RealtimeSTT import AudioToTextRecorder

class AudioInputHandler:
    def __init__(
        self, 
        model: str = "base", 
        language: str = "ru", 
        device: str = "cuda"
    ):
        print(f"🎙️ Загрузка модели распознавания речи ({model}) на {device}...")
        self.recorder = AudioToTextRecorder(
            model=model,
            language=language,
            device=device,
            silero_sensitivity=0.3,
            post_speech_silence_duration=0.6,
            min_length_of_recording=0.5,
            initial_prompt="",
        )
        print("✅ Модель готова. Ассистент слушает.")

    def listen(self) -> str:
        """
        Слушает микрофон и возвращает распознанный текст.
        Убран параметр timeout, так как он не поддерживается в вашей версии RealtimeSTT.
        """
        try:
            print("👂 Слушаю ваш запрос... (говорите)")
            # Вызываем text() без параметров
            text = self.recorder.text()
            
            if not text or text.strip() == "":
                return "Не удалось распознать речь. Попробуйте повторить."
            
            return text.strip()
            
        except Exception as e:
            return f"Ошибка при распознавании: {str(e)}"

    def shutdown(self):
        print("🛑 Остановка модуля распознавания речи...")
        self.recorder.shutdown()