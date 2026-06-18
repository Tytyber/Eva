from typing import List, Dict, Any
from openai import OpenAI
from engine.conversation import ConversationHistory
from engine.memory import LongTermMemory

class ChatHandler:
    def __init__(
        self, 
        api_key: str, 
        user_name: str = "Тутубер", 
        model: str = "poolside/laguna-m.1:free",
        memory: LongTermMemory = None
    ):
        self.client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1",)
        self.user_name = user_name
        self.model = model
        self.memory = memory
        self.history = ConversationHistory(max_messages=50)

    def respond(self, user_message: str) -> str:
        """
        Отвечает на сообщение, учитывая единую историю и долгосрочную память.
        """
        # Добавляем сообщение пользователя в единую историю
        self.history.add_user_message(user_message)
        
        # Формируем system prompt с учетом памяти
        memory_context = ""
        if self.memory:
            memory_context = self.memory.get_relevant_context(user_message)
        
        system_prompt = f"""
        Ты — дружелюбный голосовой ИИ-ассистент по имени Ева. Твой пользователь — {self.user_name}.
        
        ДОЛГОСРОЧНАЯ ПАМЯТЬ (что вы обсуждали ранее):
        {memory_context}
        
        ПРАВИЛА ДЛЯ ГОЛОСОВОГО ОБЩЕНИЯ (TTS):
        1. НИКАКИХ markdown-символов (*, #, -, списков).
        2. НИКАКИХ JSON, скобок, путей к файлам, технического жаргона.
        3. Пиши так, как будто говоришь вслух. Короткие, живые предложения.
        4. Ответ — от 1 до 4 предложений. Будь лаконичен, но дружелюбен.
        5. Обращайся к пользователю по имени, когда это уместно.
        6. Если пользователь ссылается на прошлые разговоры ("помнишь, мы говорили о..."), используй данные из ДОЛГОСРОЧНОЙ ПАМЯТИ.
        """
        
        # Собираем сообщения для LLM: system prompt + вся история
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.history.get_history())
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.8
        )
        
        assistant_message = response.choices[0].message.content.strip().strip('"')
        
        # Добавляем ответ в единую историю
        self.history.add_assistant_message(assistant_message)
        
        return assistant_message

    def get_history(self) -> ConversationHistory:
        """Возвращает единую историю для использования в других модулях."""
        return self.history