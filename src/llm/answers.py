import json
from typing import Dict, Any
from openai import OpenAI
from engine.conversation import ConversationHistory

def generate_tts_response(
    api_key: str, 
    user_request: str, 
    execution_result: Dict[str, Any], 
    user_name: str = "Тутубер",
    history: ConversationHistory = None
) -> str:
    """
    Генерирует ответ для TTS, учитывая единую историю диалога.
    """
    client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1",)
    
    # Формируем контекст истории (последние 10 сообщений)
    history_context = ""
    if history:
        recent = history.get_history()[-10:]
        history_context = "\n".join([f"{m['role']}: {m['content']}" for m in recent])
    
    system_prompt = f"""
    Ты - голосовой ИИ-ассистент. Твой пользователь - {user_name}.
    Твоя задача: кратко и естественно рассказать пользователю, что было сделано по его запросу.
    
    ИСТОРИЯ ДИАЛОГА (для контекста):
    {history_context}
    
    СТРОГИЕ ПРАВИЛА ДЛЯ ГОЛОСОВОГО ОТВЕТА (TTS):
    1. НИКАКИХ markdown-символов: никаких звездочек (*), решеток (#), списков с дефисами.
    2. НИКАКИХ путей к файлам в стиле '/home/user/script.py' или расширений '.py'. Говори "файл скрипт" или "документ".
    3. НИКАКИХ JSON-структур, скобок или технического жаргона.
    4. Пиши так, как будто ты произносишь это вслух. Используй короткие, простые предложения.
    5. Ответ должен быть от 1 до 4 предложений. Не лей воду.
    6. Если была ошибка — честно и коротко скажи, что не получилось, без технических деталей.
    7. Если пользователь ссылается на предыдущие действия ("а теперь прочитай его"), учти это из ИСТОРИИ ДИАЛОГА.
    """
    
    user_prompt = f"""
    Исходный запрос: "{user_request}"
    
    Технический отчет о выполнении:
    Статус: {execution_result.get('final_status')}
    Контекст: {json.dumps(execution_result.get('context', {}), ensure_ascii=False)}
    Лог шагов: {json.dumps(execution_result.get('log', []), ensure_ascii=False)}
    
    Напиши финальный голосовой ответ для {user_name}.
    """

    response = client.chat.completions.create(
        model="poolside/laguna-m.1:free",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip().strip('"')