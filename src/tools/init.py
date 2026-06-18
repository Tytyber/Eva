import os
import datetime
import wikipedia

def create_file(path: str, filename: str, content: str = "") -> dict:
    full_path = os.path.join(path, filename)
    os.makedirs(path, exist_ok=True)
    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "success", "message": f"Файл '{filename}' создан.", "file_path": full_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def read_file(file_path: str) -> dict:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"status": "success", "content": content}
    except Exception as e:
        return {"status": "error", "message": f"Не удалось прочитать файл: {e}"}

def get_current_time(timezone: str = "UTC") -> dict:
    now = datetime.datetime.now()
    return {"status": "success", "time": now.strftime("%Y-%m-%d %H:%M:%S"), "timezone": timezone}

def search_wikipedia(query: str, sentences: int = 2) -> dict:
    try:
        wikipedia.set_lang("ru")
        result = wikipedia.summary(query, sentences=sentences)
        return {"status": "success", "query": query, "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
def write_code_to_file(file_path: str, code: str, mode: str = "w") -> dict:
    try:
        # Получаем абсолютный путь и создаем все необходимые родительские директории
        abs_path = os.path.abspath(file_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        
        with open(abs_path, mode, encoding='utf-8') as f:
            # Если мы добавляем код (append), делаем перенос строки для красоты, если файл не пустой
            if mode == 'a' and os.path.getsize(abs_path) > 0:
                f.write('\n\n')
            f.write(code)
            
        action_text = "успешно создан и заполнен" if mode == "w" else "успешно обновлен (код добавлен)"
        return {
            "status": "success", 
            "message": f"Файл '{file_path}' {action_text}.", 
            "file_path": abs_path
        }
    except Exception as e:
        return {"status": "error", "message": f"Не удалось записать код в файл: {str(e)}"}