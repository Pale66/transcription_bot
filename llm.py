from datetime import datetime
from httpx import AsyncClient
from config import LLM_MODEL_PATH

LLAMA_ARGS = [
    "-fa",
    "on",
    "-rea",
    "off",
    "-m",
    str(LLM_MODEL_PATH),
    "--sleep-idle-seconds",
    "10",
    "-t",
    "6",
]
COMPLETIONS_URL = r"http://127.0.0.1:5001/v1/chat/completions"


async def request_summary(text: str, http_client: AsyncClient) -> str:
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
    response = await http_client.post(COMPLETIONS_URL, json=data_json)
    response.raise_for_status()
    response_json = response.json()
    print("Prompt proccesed in ", datetime.now() - start)
    return response_json["choices"][0]["message"]["content"]
