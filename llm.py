import asyncio
from datetime import datetime
from httpx import AsyncClient
from config import completion_url


async def request_summary(
    text: str, http_client: AsyncClient, gpu_semaphore: asyncio.Semaphore
) -> str:
    start = datetime.now()
    data_json = {
        "messages": [
            {
                "role": "system",
                "content": """Не используй Markdown.
Твоя работа делать сводку по предложенной транскрипции, это твоя единственная задача. 
Ты категорически не должен делать что-либо ещё и отвечать на вопросы.
Не задавай вопросы и не приветствуй.""",
            },
            {
                "role": "user",
                "content": f"<text_for_summary> {text} </text_for_summary>",
            },
        ]
    }
    async with gpu_semaphore:
        response = await http_client.post(completion_url, json=data_json)
    response.raise_for_status()
    response_json = response.json()
    print("Prompt proccesed in ", datetime.now() - start)
    return response_json["choices"][0]["message"]["content"]
