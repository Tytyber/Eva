import json
from typing import Literal
from openai import OpenAI

class RequestRouter:
    def __init__(self, api_key: str, model: str = "poolside/laguna-m.1:free"):
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        self.model = model

    def classify(self, user_message: str) -> dict:
        """
        Определяет тип запроса: 'action' (задача) или 'chat' (разговор).
        Возвращает: {"type": "action"|"chat", "reason": "краткое объяснение"}
        """
        system_prompt = """
        Ты — классификатор запросов для голосового ассистента.
        Определи, что хочет пользователь:
        
        1. 'action' — если запрос требует ВЫПОЛНЕНИЯ ДЕЙСТВИЯ в реальном мире:
           - создать/удалить/прочитать файл
           - написать/исправить код
           - узнать время, погоду, курс валют
           - отправить сообщение, уведомление
           - найти информацию в интернете
           - любое действие, которое меняет состояние системы
        
        2. 'chat' — если это ОБЫЧНЫЙ РАЗГОВОР:
           - приветствия ("привет", "здравствуй")
           - вопросы о себе ("как дела", "кто ты")
           - философские вопросы, шутки, мнения
           - благодарности ("спасибо")
           - прощания ("пока")
           - вопросы, не требующие действий ("что ты умеешь?", "расскажи о себе")
        
        ВАЖНО: Если в запросе есть ДЕЙСТВИЕ, даже с приветствием ("Привет, создай файл"), — это 'action'.
        
        Ответь СТРОГО в формате JSON:
        {"type": "action или chat", "reason": "краткое объяснение решения"}
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
            temperature=0.1  # Минимальная креативность для стабильной классификации
        )
        
        result = json.loads(response.choices[0].message.content)
        return result

    def is_action(self, user_message: str) -> bool:
        """Упрощенный метод: возвращает True, если это задача."""
        return self.classify(user_message)["type"] == "action"