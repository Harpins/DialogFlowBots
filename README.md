# DialogFlowBots
Проект содержит два независимых чат-бота (для Telegram и VK-сообществ), использующих Google Dialogflow ES для обработки сообщений.  
Боты отвечают только на сообщения, которые уверенно распознает Dialogflow. Для ВК при fallback-интенте или пустом ответе бот **будет молчать** (сделано намеренно).

Также включён скрипт автоматической загрузки интентов из JSON-файла в Dialogflow (на русском языке).

## Установка

1. Клонируйте репозиторий
```bash
git clone https://github.com/ваш-логин/your-dialogflow-bots.git
cd your-dialogflow-bots
```

2. Установите зависимости
```bash
pip install -r requirements.txt
```
или вручную:
```bash
pip install aiogram vk_api google-cloud-dialogflow environs
```

### Доступ к Dialogflow

В Google Cloud Console создайте сервисный аккаунт с ролью Dialogflow API Admin.
Скачайте JSON-ключ и положите его в корень проекта под именем dialogflow-key.json.
Убедитесь, что в вашем Dialogflow-агенте добавлен русский язык (Settings → Languages → + Russian (ru)).

### Переменные окружения

```bash
TG_BOT_TOKEN=ваш_токен_телеграм_бота
VK_GROUP_TOKEN=токен_сообщества_вк
PROJECT_ID=ваш_google_cloud_project_id  
LANGUAGE_CODE=ru-RU
JSON_PATH=путь_до_json_файла_с_интентами
GOOGLE_APPLICATION_CREDENTIALS=полный_путь_до_json_файла_авторизации_google_cloud
```

## Загрузка интентов
Интенты загружаются в русскую версию агента.
В корневой папке расположите json-файл (название по дефолту `intents.json`) следующей структуры:
```bash
{
  "Приветствие": {
    "questions": ["привет", "здравствуйте", "добрый день"],
    "answer": ["Привет! Чем могу помочь?", "Здравствуйте!"]
  },
  "Как дела": {
    "questions": ["как дела", "как жизнь"],
    "answer": "Отлично, спасибо! А у тебя?"
  }
}
```
Вызовите функцию `load_intents_from_json(PROJECT_ID, JSON_PATH)` из скрипта `dialogflowapi.py`

## Запуск ботов
```bash
python bot_telegram.py
python bot_vk.py
```
Боты друг от друга независимы