import os
import requests

from dotenv import load_dotenv
load_dotenv()

class AIIntegration:

    def generate_dream_steps(self, prompt: str) -> list[dict[str, str | int]]:
        api_key = os.getenv('OPENROUTER_API_KEY')
        url = 'https://openrouter.ai/api/v1/chat/completions'
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "qwen/qwen3-235b-a22b-07-25:free",
            "messages": [
                {
                    "role": "user",
                    "content": f"""Разбей мечту '{prompt}' на минимум 5 конкретных шагов,
                    если можно разбить на больше - делай, каждый шаг в виде короткой фразы
                    + сложность данной подцели от 1 до 3.
                    формат ответа следующий:
                    Сделать так так | 1
                    ... | 2"""
                }
            ],
            "max_tokens": 500,
        }
        response = requests.post(url, headers=headers, json=data)
        # print(response.status_code, '\n', response.json())
        choices = response.json().get("choices", [])
        if not choices or response.status_code != 200:
            return []
        
        text = choices[0]["message"]["content"]
        res = []
        for line in text.split('\n'):
            line = line.split('|')
            res.append({'text': line[0].strip(), 'difficulty': int(line[1].strip())})
        return res