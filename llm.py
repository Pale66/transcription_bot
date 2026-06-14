from time import sleep
from datetime import datetime
import subprocess
import atexit
import requests as r
import json
import asyncio
import aiohttp
from config import LLM_MODEL_PATH, LLAMA_BIN

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
COMPLETIONS_URL = r"http://127.0.0.1:8080/v1/chat/completions"


def start_llama():
    llama_instance = subprocess.Popen(
        args=[str(LLAMA_BIN), *LLAMA_ARGS],
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
    )
    atexit.register(llama_instance.terminate)


'''
def request_summary(text: str) -> str:
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
    llama_request = r.post(url=COMPLETIONS_URL, json=data_json)
    print("Prompt proccesed in ", datetime.now() - start)
    if llama_request.status_code == 200:
        response_json = json.loads(llama_request.text)
        return response_json["choices"][0]["message"]["content"]
    else:
        return "Some error"
    '''


async def request_summary(text: str) -> str:
    start = datetime.now()
    async with aiohttp.ClientSession() as session:
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
        async with session.post(COMPLETIONS_URL, json=data_json) as response:
            if response.status == 200:
                response_json = await response.json()
                print("Prompt proccesed in ", datetime.now() - start)
                return response_json["choices"][0]["message"]["content"]
            else:
                return "Some error"


if __name__ == "__main__":
    start_llama()
    while True:
        while True:
            try:
                health = r.get("http://127.0.0.1:8080/health", timeout=1)

                if health.status_code == 200:
                    break

            except r.RequestException:
                pass

            sleep(1)
        print(request_summary(input("Вводи текст\n")))
