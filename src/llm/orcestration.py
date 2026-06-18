import inspect
import json
from typing import Dict, Any, Callable
from openai import OpenAI

class AgentOrchestrator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.tools: Dict[str, Callable] = {}
        self.context: Dict[str, Any] = {}

    def register_tool(self, name: str, func: Callable):
        self.tools[name] = func

    def _route_tool(self, action: str, target: str) -> str:
        action = action.lower()
        target = target.lower()
        
        if "создать" in action and "файл" in target:
            return "create_file"
        elif "прочитать" in action or "читать" in action:
            return "read_file"
        elif "время" in target or "время" in action:
            return "get_current_time"
        elif "найти" in action or "поиск" in action:
            return "search_wikipedia"
        elif ("написать" in action or "записать" in action or "добавить" in action) and \
             ("код" in target or "функци" in target or "скрипт" in target or "файл" in target):
            return "write_code_to_file"
            
        raise ValueError(f"Не удалось сопоставить действие '{action}' и цель '{target}' с известными инструментами.")

    def _extract_args_with_llm(self, details: str, tool_name: str, tool_func: Callable) -> Dict[str, Any]:
        sig = inspect.signature(tool_func)
        doc = inspect.getdoc(tool_func) or "Описание отсутствует."
        
        system_prompt = f"""
        Ты - система извлечения аргументов.
        Функция: {tool_name}
        Сигнатура: {sig}
        Документация: {doc}
        Верни СТРОГО валидный JSON. Ключи должны совпадать с параметрами функции.
        """
        
        context_str = json.dumps(self.context, ensure_ascii=False) if self.context else "Контекст пуст."
        user_prompt = f"Задача: '{details}'\nКонтекст: {context_str}"

        response = self.client.chat.completions.create(
            model="poolside/laguna-m.1:free",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        args = json.loads(response.choices[0].message.content)
        return {k: v for k, v in args.items() if v is not None}

    def execute_plan(self, plan: dict) -> dict:
        """
        Выполняет план БЕЗ дополнительных LLM-вызовов.
        Аргументы уже извлечены в plan["steps"][i]["arguments"]
        """
        steps = plan.get("steps", [])
        completed_steps = set()
        execution_log = []
        
        print(f"🚀 Начало выполнения: {plan.get('main_intent')}")
        
        while len(completed_steps) < len(steps):
            ready_steps = [
                s for s in steps 
                if s["step_id"] not in completed_steps 
                and all(dep in completed_steps for dep in s.get("dependencies", []))
            ]
            
            if not ready_steps:
                break
            
            step = ready_steps[0]
            tool_name = step["tool_name"]
            args = step["arguments"]  # ← Аргументы уже готовы!
            
            print(f"⚙️ Шаг {step['step_id']}: {tool_name}({args})")
            
            try:
                tool_func = self.tools[tool_name]
                result = tool_func(**args)
                
                if result.get("status") == "success":
                    print(f"✅ Успех: {result.get('message')}")
                    completed_steps.add(step["step_id"])
                    
                    if "file_path" in result:
                        self.context["last_created_file"] = result["file_path"]
                        
                    execution_log.append({"step_id": step["step_id"], "status": "success", "result": result})
                else:
                    print(f"❌ Ошибка: {result.get('message')}")
                    execution_log.append({"step_id": step["step_id"], "status": "failed"})
                    break
                    
            except Exception as e:
                print(f"❌ Критическая ошибка: {e}")
                execution_log.append({"step_id": step["step_id"], "status": "error"})
                break
        
        return {
            "final_status": "success" if len(completed_steps) == len(steps) else "failed",
            "log": execution_log,
            "context": self.context
        }