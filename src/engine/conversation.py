from typing import List, Dict, Any
import json

class ConversationHistory:
    def __init__(self, max_messages: int = 50):
        self.messages: List[Dict[str, str]] = []
        self.max_messages = max_messages

    def add_user_message(self, content: str):
        """Добавляет сообщение пользователя."""
        self.messages.append({"role": "user", "content": content})
        self._trim()

    def add_assistant_message(self, content: str):
        """Добавляет ответ ассистента."""
        self.messages.append({"role": "assistant", "content": content})
        self._trim()

    def add_system_event(self, event_type: str, details: str):
        """
        Добавляет системное событие (например, результат выполнения задачи).
        Это невидимо для пользователя, но ассистент это видит.
        """
        self.messages.append({
            "role": "system",
            "content": f"[СОБЫТИЕ: {event_type}] {details}"
        })
        self._trim()

    def get_history(self) -> List[Dict[str, str]]:
        """Возвращает полную историю для передачи в LLM."""
        return self.messages.copy()

    def _trim(self):
        """Ограничивает размер истории."""
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def clear(self):
        """Очищает историю."""
        self.messages = []

    def to_json(self) -> str:
        """Сериализует историю в JSON (для отладки)."""
        return json.dumps(self.messages, ensure_ascii=False, indent=2)