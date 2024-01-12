import logging
import os
import random

from dotenv import load_dotenv
import redis
import vk_api as vk
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from questions import get_questions


logger = logging.getLogger('QUIZ_bot VK')


def reply_from_vk_bot(user_id, message):
    keyboard = VkKeyboard()
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.SECONDARY)

    vk_session.method('messages.send', {
        'user_id': user_id,
        'message': message,
        'random_id': get_random_id(),
        'keyboard': keyboard.get_keyboard(),
    })


def get_answer_from_user(event, user_id, redis_db):
    if event.text.lower() in redis_db.get(user_id).decode().lower() and len(event.text) > 1:
        logger.info(f'Пользователь {user_id} - Получен верный ответ')
        user_result = int(redis_db.get(f'{user_id}_result').decode()) + 1
        redis_db.set(f'{user_id}_result', user_result)
        reply_from_vk_bot(user_id, 'Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос"')
    else:
        logger.info(f'Пользователь {user_id} - Получен не верный ответ')
        reply_from_vk_bot(user_id, 'Неправильно… Попробуешь ещё раз?')


if __name__ == "__main__":
    load_dotenv()
    vk_session = vk.VkApi(token=os.getenv('VK_TOKEN'))
    redis_db = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'))

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger.setLevel(logging.INFO)

    questions = get_questions()

    for event in VkLongPoll(vk_session).listen():
        if not (event.type == VkEventType.MESSAGE_NEW and event.to_me):
            continue
        user_id = event.user_id
        if redis_db.get(f'{user_id}_result') is None:
            redis_db.set(f'{user_id}_result', 0)
        if event.text == 'Новый вопрос':
            logger.info(f'Пользователь {user_id} - Запрошен новый вопрос')
            question = random.choice(questions)
            redis_db.set(user_id, question['answer'])
            reply_from_vk_bot(user_id, question['question'])
            continue
        if event.text == 'Сдаться':
            logger.info(f'Пользователь {user_id} - Сдался')
            message = f'Вот тебе правильный ответ - {redis_db.get(user_id).decode()} Чтобы продолжить - нажми ' \
                      f'"Новый вопрос"'
            reply_from_vk_bot(user_id, message)
            continue
        if event.text == 'Мой счёт':
            logger.info(f'Пользователь {user_id} - запрошен счет')
            message = f'Количество правильных ответов - {redis_db.get(f"{user_id}_result").decode()}'
            reply_from_vk_bot(user_id, message)
            continue
        get_answer_from_user(event, user_id, redis_db)

