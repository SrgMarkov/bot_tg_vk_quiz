import logging
import os
import random

import redis
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

from questions import get_questions


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger('QUIZ_bot TG')


QUESTIONS = []
QUESTION, ANSWER, RESULT, REDIS = range(4)


def get_keyboard() -> ReplyKeyboardMarkup:
    quiz_keyboard = [['Новый вопрос', 'Сдаться'],
                     ['Мой счёт']]
    return ReplyKeyboardMarkup(quiz_keyboard, resize_keyboard=True)


def start(update: Update, context: CallbackContext):
    logger.info("Получена команда start")
    update.message.reply_text(
        'Привет! Я квиз-БОТ, помогу тебе проверить уровень твоих знаний. '
        'Если хочешь закончить диалог - введи команду /exit',
        reply_markup=get_keyboard()
    )
    context.user_data['score'] = 0
    return QUESTION


def handle_new_question_request(update: Update, context: CallbackContext):
    context.user_data['user_id'] = update.message.from_user.id
    logger.info(f'Пользователь {context.user_data["user_id"]} - Запрошен новый вопрос')
    question = random.choice(QUESTIONS)
    update.message.reply_text(text=question['question'], reply_markup=get_keyboard())
    REDIS.set(context.user_data['user_id'], question['answer'])
    return ANSWER


def handle_solution_attempt(update: Update, context: CallbackContext):
    logger.info(f'Пользователь {context.user_data["user_id"]} - Ожидание ответа')
    user_answer = update.message.text
    correct_answer = REDIS.get(context.user_data['user_id']).decode()
    if user_answer.lower() in correct_answer.lower() and len(user_answer) > 1:
        logger.info(f'Пользователь {context.user_data["user_id"]} - Получен верный ответ')
        update.message.reply_text(text='Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос"',
                                  reply_markup=get_keyboard())
        context.user_data['score'] += 1
        return QUESTION
    elif user_answer == 'Сдаться':
        logger.info(f'Пользователь {context.user_data["user_id"]} - Сдался')
        loose_text = f'Вот тебе правильный ответ - {correct_answer} Чтобы продолжить - нажми "Новый вопрос"'
        update.message.reply_text(text=loose_text)
        return QUESTION
    else:
        logger.info(f'Пользователь {context.user_data["user_id"]} - Получен не верный ответ')
        update.message.reply_text(text='Неправильно… Попробуешь ещё раз?')
        return ANSWER


def handle_user_results(update: Update, context: CallbackContext):
    logger.info(f'Пользователь {context.user_data["user_id"]} - запрошен счет')
    update.message.reply_text(text=f'Количество правильных ответов -  {context.user_data["score"]}')
    return QUESTION


def stop_bot(update: Update, context: CallbackContext):
    update.message.reply_text('Пока! До новых встреч!',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


if __name__ == '__main__':
    load_dotenv()

    updater = Updater(os.getenv('TELEGRAM_BOT_TOKEN'))
    dp = updater.dispatcher

    REDIS = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'))
    questions = get_questions()

    QUESTIONS = get_questions()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION: [MessageHandler(Filters.regex('^(Новый вопрос)$'), handle_new_question_request),
                       MessageHandler(Filters.regex('^(Мой счёт)$'), handle_user_results),
                       ],
            ANSWER: [MessageHandler(Filters.text, handle_solution_attempt)],
        },
        fallbacks=[CommandHandler('exit', stop_bot)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()
