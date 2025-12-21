import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from settings import VK_GROUP_TOKEN
from vk_api.utils import get_random_id  
from logger import get_logger

logger = get_logger(__name__)

def echo(event, vk_api):
    user_id = event.user_id
    user_message = event.text

    if not user_message:
        return  

    try:
        vk_api.messages.send(
            user_id=user_id,
            message=user_message,  
            random_id=get_random_id()  
        )
    except vk_api.exceptions.ApiError as e:
        if e.code == 901:
            logger.error(f"Ошибка 901: Пользователь {user_id} не разрешил сообщения боту.")
        elif e.code == 902:
            logger.error(f"Ошибка 902: Бот заблокирован пользователем {user_id}")
        else:
            logger.error(f"Ошибка VK API [{e.code}]: {e.error_msg}")


if __name__ == "__main__":
    vk_session = vk.VkApi(token=VK_GROUP_TOKEN)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    logger.info("Бот запущен и слушает сообщения...")

    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                echo(event, vk_api)
    except Exception as e:
        logger.error(f"Критическая ошибка longpoll: {e}")