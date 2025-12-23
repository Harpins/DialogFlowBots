import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from settings import VK_GROUP_TOKEN, PROJECT_ID
from vk_api.utils import get_random_id
from logger import get_logger
from dialogflowapi import detect_intent_text
from error_bot import send_error_bot_note_sync

logger = get_logger(__name__)


def send_vk_message(vk_api, user_id, message_text):
    if not message_text:
        logger.warning("Текст сообщения не передан на отправку")
        return
    try:
        vk_api.messages.send(
            user_id=user_id, message=message_text, random_id=get_random_id()
        )
    except vk_api.exceptions.ApiError as e:  
        if e.code == 901:
            logger.warning(
                f"Ошибка 901: Пользователь {user_id} не разрешил сообщения боту."
            )
        elif e.code == 902:
            logger.warning(f"Ошибка 902: Бот заблокирован пользователем {user_id}")
        elif e.code == 15:
            logger.warning(f"Ошибка 15: Бот в черном списке у пользователя {user_id}")
        else:
            err_msg = f"Ошибка VK API [{e.code}]: {e.error_msg} (пользователь {user_id})"
            logger.error(err_msg)
            send_error_bot_note_sync(err_msg)


def handle_message(event, vk_api, project_id=PROJECT_ID):
    user_id = event.user_id
    user_message = event.text.strip()

    if not user_message:
        return

    logger.info(f"Сообщение от пользователя {user_id}: {user_message}")

    session_id = f"vk_{user_id}"

    df_response = detect_intent_text(
        project_id=project_id,
        session_id=session_id,
        text=user_message,
        language_code="ru-RU",
    )

    answer_text = df_response.get("answer_text", "").strip()
    fallback = df_response.get("is_fallback", False)
    if not answer_text:
        warning_text = f"DF не вернул ответ на сообщение '{user_message}' пользователя '{user_id}'"
        logger.warning(warning_text)
        send_error_bot_note_sync(warning_text)
        return
    if fallback:
        logger.info(f"Fallback-интент для пользователя {user_id}")
        return
    send_vk_message(vk_api, user_id, answer_text)
    return


if __name__ == "__main__":
    vk_session = vk.VkApi(token=VK_GROUP_TOKEN)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    logger.info("VK-бот с Dialogflow запущен и слушает сообщения...")

    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                handle_message(event, vk_api)
    except KeyboardInterrupt:
        logger.info("Бот остановлен вручную.")
    except Exception as e:
        err_msg = f"Критическая ошибка VK longpoll: {e}"
        logger.critical(err_msg, exc_info=True)
        send_error_bot_note_sync(err_msg)
