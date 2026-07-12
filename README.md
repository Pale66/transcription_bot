# Telegram Media Assistant Bot

Telegram-бот для расшифровки и краткого пересказа медиа контента

## Возможности

- Транскрипция:
  - голосовых сообщений
  - аудио
  - видео
  - видео кружков
  - медиа по URL (через `yt-dlp`)
- Вывод транскрипции с таймкодами или без
- Краткое содержание транскрипции с помощью LLM
- Кэширование результатов транскрипции для повторных запросов

## Используемые технологии

- Python 3.13+
- aiogram 3
- httpx
- yt-dlp

Бот взаимодействует с внешними HTTP API:

- OpenAI-compatible Whisper API — распознавание речи
- OpenAI-compatible Chat Completions API — генерация краткого содержания.

## Конфигурация

Создайте `config.json` по примеру `config.example.json`.

Также необходимо задать переменную окружения:

```text
BOT_TOKEN=<telegram_bot_token>
```

## Запуск

```
python -m venv .venv
.venv/scripts/activate
pip install -r requirements.txt
python main.py
```

Перед запуском убедитесь, что сервисы Whisper и LLM доступны по адресам,
указанным в `config.json`.

## Лицензия

MIT
