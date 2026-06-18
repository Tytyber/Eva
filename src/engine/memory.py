import json
import os
from datetime import datetime
from typing import List, Dict, Any
from openai import OpenAI

class LongTermMemory:
    def __init__(self, api_key: str, memory_file: str = "memory.json", model: str = "poolside/laguna-m.1:free"):
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        self.memory_file = memory_file
        self.model = model
        self.topics: List[Dict[str, Any]] = self._load_memory()

    def _load_memory(self) -> List[Dict[str, Any]]:
        """Загружает сохраненные темы из файла."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Ошибка загрузки памяти: {e}")
        return []

    def _save_memory(self):
        """Сохраняет темы в файл."""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.topics, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  Ошибка сохранения памяти: {e}")

    def extract_and_save_topics(self, user_message: str, assistant_response: str, context: Dict[str, Any] = None):
        system_prompt = """
        Ты — система анализа диалогов. Твоя задача: извлечь из разговора ключевые темы и сохранить их для будущей памяти ассистента.
        
        Правила:
        1. Выдели 1-3 основные темы разговора (например: "программирование", "файлы", "время", "шутка").
        2. Напиши краткое резюме (1-2 предложения) о том, что обсуждалось или было сделано.
        3. Если это была задача (создание файла, написание кода), укажи, что именно было сделано.
        4. Если это обычный разговор, укажи тему беседы.
        
        Ответь СТРОГО в формате JSON:
        {
          "topics": ["тема1", "тема2"],
          "summary": "Краткое описание того, о чем говорили или что было сделано"
        }
        """
        
        user_prompt = f"""
        Пользователь: "{user_message}"
        Ассистент: "{assistant_response}"
        Контекст выполнения: {json.dumps(context or {}, ensure_ascii=False)}
        
        Извлеки темы и напиши резюме.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Добавляем в память
            memory_entry = {
                "timestamp": datetime.now().isoformat(),
                "topics": result.get("topics", []),
                "summary": result.get("summary", ""),
                "user_message": user_message[:100],  # Обрезаем для экономии места
                "assistant_response": assistant_response[:100]
            }
            
            self.topics.append(memory_entry)
            
            # Ограничиваем память последними 100 записями
            if len(self.topics) > 100:
                self.topics = self.topics[-100:]
            
            self._save_memory()
            print(f"Память обновлена: темы={result.get('topics', [])}")
            
        except Exception as e:
            print(f"Ошибка извлечения тем: {e}")

    def get_relevant_context(self, current_message: str, max_topics: int = 10) -> str:
        """
        Возвращает релевантные темы из памяти для передачи в контекст LLM.
        В простой реализации возвращаем последние N записей.
        Для настоящего RAG здесь был бы поиск по эмбеддингам.
        """
        if not self.topics:
            return "Память пуста. Это начало разговора."
        
        # Берем последние записи (в продвинутой версии здесь был бы поиск по схожести)
        recent = self.topics[-max_topics:]
        
        context_parts = []
        for entry in recent:
            topics_str = ", ".join(entry.get("topics", []))
            summary = entry.get("summary", "")
            context_parts.append(f"- Темы: {topics_str}. Резюме: {summary}")
        
        return "\n".join(context_parts)

    def clear_memory(self):
        """Очищает всю память."""
        self.topics = []
        self._save_memory()
        print("🗑️  Память очищена")