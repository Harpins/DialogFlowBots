from google.cloud import dialogflow_v2 as dialogflow
from logger import get_logger
import json
from settings import PROJECT_ID, JSON_PATH

logger = get_logger(__name__)

def detect_intent_text(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
   
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    
    response = session_client.detect_intent(session=session, query_input=query_input)
    query_result = {
        'answer_text': response.query_result.fulfillment_text,
        'is_fallback': response.query_result.intent.is_fallback
    }

    return query_result


def create_intent(project_id, display_name, training_phrases_parts, message_texts, language_code="ru"):
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)

    training_phrases = []
    for phrase in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=phrase)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message]
    )

    try:
        response = intents_client.create_intent(
            request={"parent": parent, "intent": intent, "language_code": language_code}
        )
        logger.info(f"Интент успешно создан: {response.name} ({display_name})")
        return response
    except Exception as e:
        logger.error(f"Ошибка при создании интента '{display_name}': {e}", exc_info=True)
        raise
    

def load_intents_from_json(project_id, json_file_path="intents.json"):
    """   
    Формат JSON:
    {
        "Название интента 1": {
            "questions": ["вопрос 1", "вопрос 2", ...],
            "answer": ["ответ 1", "ответ 2"] или "один ответ"
        },
        "Название интента 2": { ... }
    }
    """
    try:
        with open(json_file_path, "r", encoding="utf-8") as file:
            intents_dict = json.load(file)
        logger.info(f"Загружено {len(intents_dict)} интентов из {json_file_path}")
    except FileNotFoundError:
        logger.error(f"Файл {json_file_path} не найден.")
        return
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка разбора JSON: {e}")
        return

    successful = 0
    skipped = 0

    for display_name, data in intents_dict.items():
        questions = data.get("questions", [])
        answer = data.get("answer", [])

        if isinstance(answer, str):
            message_texts = [answer]
        elif isinstance(answer, list):
            message_texts = [text for text in answer if isinstance(text, str)]
        else:
            message_texts = []

        if not questions:
            logger.warning(f"Пропуск интента '{display_name}': нет тренировочных фраз.")
            skipped += 1
            continue

        if not message_texts:
            logger.warning(f"Пропуск интента '{display_name}': нет текста ответа.")
            skipped += 1
            continue

        logger.info(f"Пытаемся создать интент: {display_name}")

        try:
            create_intent(
                project_id=project_id,
                display_name=display_name,
                training_phrases_parts=questions,
                message_texts=message_texts
            )
            successful += 1
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.warning(f"Интент с названием {display_name}' уже существует — пропускаем.")
                skipped += 1
            else:
                logger.error(f"Не удалось создать интент '{display_name}'")
                skipped += 1

    logger.info(f"Загрузка интентов завершена: успешно — {successful}, пропущено — {skipped}")
    
    
#load_intents_from_json(PROJECT_ID, JSON_PATH)