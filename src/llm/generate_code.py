from openai import OpenAI

def generate_code(prompt, api_key):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    response = client.chat.completions.create(
        model="qwen/qwen3-coder:free",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content