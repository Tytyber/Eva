import json
from openai import OpenAI
from typing import Dict, Any

def extract_user_intents(api_key: str, user_prompt: str) -> dict:
    """
    Распознает намерение И СРАЗУ извлекает аргументы для всех шагов.
    """
    from openai import OpenAI
    import json
    import tools.init as tools
    
    client = OpenAI(api_key=api_key)
    
    # Получаем сигнатуры всех инструментов
    tool_schemas = []
    for name, func in tools.__dict__.items():
        if callable(func) and hasattr(func, '__doc__'):
            import inspect
            sig = inspect.signature(func)
            doc = inspect.getdoc(func) or ""
            tool_schemas.append(f"- {name}{sig}: {doc}")
    
    tools_str = "\n".join(tool_schemas)
    
    system_prompt = f"""
Ты - система планирования задач для голосового ассистента.

ДОСТУПНЫЕ ИНСТРУМЕНТЫ:
{tools_str}

ЗАДАЧА:
1. Проанализируй запрос пользователя
2. Разбей его на шаги
3. Для КАЖДОГО шага СРАЗУ извлеки аргументы для вызова инструмента

Ответь СТРОГО в формате JSON:
{{
  "main_intent": "Краткое описание",
  "steps": [
    {{
      "step_id": 1,
      "tool_name": "имя_функции_из_списка",
      "arguments": {{"param1": "value1", "param2": "value2"}},
      "dependencies": []
    }}
  ]
}}

ВАЖНО:
- Используй ТОЛЬКО функции из списка выше
- Аргументы должны точно соответствовать сигнатуре функции
- Если запрос не требует действий (приветствие, вопрос), верни {{"steps": []}}
"""
    
    response = client.chat.completions.create(
        model="google/gemma-3-12b-it:free",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    
    return json.loads(response.choices[0].message.content)