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


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger('QUIZ_bot VK')


def get_vk_keyboard():
    keyboard = VkKeyboard()
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()


if __name__ == "__main__":
    load_dotenv()
    vk_session = vk.VkApi(token=os.getenv('VK_TOKEN'))
    redis = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'))
    questions = get_questions()
    user_results = 0

    for event in VkLongPoll(vk_session).listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            if event.text == 'Новый вопрос':
                logger.info(f'Пользователь {user_id} - Запрошен новый вопрос')
                question = random.choice(questions)
                redis.set(user_id, question['answer'])
                print(question)
                vk_session.method('messages.send', {
                    'user_id': user_id,
                    'message': question['question'],
                    'random_id': get_random_id(),
                    'keyboard': get_vk_keyboard(),
                })
            elif event.text == 'Сдаться':
                logger.info(f'Пользователь {user_id} - Сдался')
                vk_session.method('messages.send', {
                    'user_id': user_id,
                    'message': f'Вот тебе правильный ответ - {redis.get(user_id).decode()} Чтобы продолжить - нажми '
                               f'"Новый вопрос"',
                    'random_id': get_random_id(),
                    'keyboard': get_vk_keyboard(),
                })
            elif event.text == 'Мой счёт':
                logger.info(f'Пользователь {user_id} - запрошен счет')
                vk_session.method('messages.send', {
                    'user_id': user_id,
                    'message': f'Количество правильных ответов - {user_results}',
                    'random_id': get_random_id(),
                    'keyboard': get_vk_keyboard(),
                })
            else:
                if event.text.lower() in redis.get(user_id).decode().lower() and len(event.text) > 1:
                    logger.info(f'Пользователь {user_id} - Получен верный ответ')
                    user_results += 1
                    vk_session.method('messages.send', {
                        'user_id': user_id,
                        'message': 'Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос"',
                        'random_id': get_random_id(),
                        'keyboard': get_vk_keyboard(),
                    })
                else:
                    logger.info(f'Пользователь {user_id} - Получен не верный ответ')
                    vk_session.method('messages.send', {
                        'user_id': user_id,
                        'message': 'Неправильно… Попробуешь ещё раз?',
                        'random_id': get_random_id(),
                        'keyboard': get_vk_keyboard(),
                    })

