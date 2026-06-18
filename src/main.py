from llm.orcestration import AgentOrchestrator
from llm.dialog_answer import ChatHandler
from engine.memory import LongTermMemory
from audio.audio_engine import AudioInputHandler
from audio.tts_engine import TTSEngine
from engine.intent_classifier import extract_user_intents
import tools.init as tools
import time
import threading

API_KEY = "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"

class VoiceAssistant:
    def __init__(self, api_key: str, user_name: str = "Тутубер"):
        self.user_name = user_name
        self.api_key = api_key
        
        self.audio_input = AudioInputHandler(model="base", language="ru", device="cuda")
        self.tts = TTSEngine()
        self.memory = LongTermMemory(api_key=api_key, memory_file="assistant_memory.json")
        self.chat = ChatHandler(api_key=api_key, user_name=user_name, memory=self.memory)
        self.orchestrator = AgentOrchestrator(api_key=api_key)
        
        self.orchestrator.register_tool("create_file", tools.create_file)
        self.orchestrator.register_tool("read_file", tools.read_file)
        self.orchestrator.register_tool("get_current_time", tools.get_current_time)
        self.orchestrator.register_tool("write_code_to_file", tools.write_code_to_file)
        
    def process_text_request(self, user_message: str) -> str:
        print(f"\n📝 Распознанный текст: '{user_message}'")
        
        # ОДИН LLM-вызов вместо четырех
        try:
            plan = extract_user_intents(api_key=self.api_key, user_prompt=user_message)
            
            if plan.get("type") == "action" and plan.get("steps"):
                print("⚙️ Режим: ВЫПОЛНЕНИЕ ЗАДАЧИ")
                response = self._handle_action_with_plan(user_message, plan)
            else:
                print("💬 Режим: РАЗГОВОР")
                response = plan.get("voice_response") or self.chat.respond(user_message)
                self.chat.get_history().add_user_message(user_message)
                self.chat.get_history().add_assistant_message(response)
                
        except Exception as e:
            print(f"💬 Режим: РАЗГОВОР (ошибка: {e})")
            response = self.chat.respond(user_message)
        
        # Асинхронное сохранение в память
        self._save_memory_async(user_message, response)
        
        return response

    def _handle_action_with_plan(self, user_message: str, plan: dict) -> str:
        self.chat.get_history().add_user_message(user_message)
        
        # Озвучиваем начало СРАЗУ
        voice_intro = plan.get("voice_response", "Хорошо, выполняю.")
        self.tts.speak(voice_intro)
        
        # Выполняем задачу
        execution_result = self.orchestrator.execute_plan(plan)
        
        # Финальный ответ
        if execution_result["final_status"] == "success":
            voice_final = f"{self.user_name}, задача выполнена."
        else:
            voice_final = f"Извини, возникла ошибка."
        
        self.chat.get_history().add_assistant_message(voice_intro + " " + voice_final)
        return voice_final

    def _save_memory_async(self, user_message: str, response: str):
        def save():
            try:
                self.memory.extract_and_save_topics(
                    user_message=user_message,
                    assistant_response=response,
                    context=self.orchestrator.context
                )
            except Exception as e:
                print(f"⚠️ Ошибка памяти: {e}")
        
        threading.Thread(target=save, daemon=True).start()

    def run_voice_loop(self):
        print("\n" + "="*60)
        print(f"🎙️ БЫСТРЫЙ АССИСТЕНТ АКТИВИРОВАН")
        print("="*60)
        
        try:
            while True:
                user_text = self.audio_input.listen()
                
                if user_text.lower() in ["стоп", "выход", "хватит", "пока"]:
                    self.tts.speak(f"До свидания, {self.user_name}.")
                    break
                
                response_text = self.process_text_request(user_text)
                
                # Озвучиваем только если это не задача (для задачи уже озвучили)
                if "задача выполнена" not in response_text.lower() and "выполняю" not in response_text.lower():
                    self.tts.speak(response_text)
                
                time.sleep(0.3)
                
        except KeyboardInterrupt:
            print("\n⚠️ Прервано")
        finally:
            self.audio_input.shutdown()


if __name__ == "__main__":
    assistant = VoiceAssistant(api_key=API_KEY, user_name="Тутубер")
    assistant.run_voice_loop()