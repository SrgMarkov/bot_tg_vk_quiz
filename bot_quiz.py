import logging
import os

from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

from handler import BotLogsHandler

logger_tg = logging.getLogger('quiz_bot_tg')


def start(update: Update, context) -> None:
    update.message.reply_text(
        'Привет! Проверим твои знания'
    )


def help_handler(update: Update, context) -> None:
    update.message.reply_text(
        '''help '''
    )


def make_answer(update, context) -> None:
    update.message.reply_text(update.message.text)


if __name__ == '__main__':
    load_dotenv()
    tg_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TG_ADMIN_ID')
    bot = Bot(tg_token)

    updater = Updater(tg_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help_handler))
    dispatcher.add_handler(MessageHandler(Filters.text, make_answer))

    logging.basicConfig(format="%(process)d %(levelname)s %(message)s")
    logger_tg.setLevel(logging.INFO)
    logger_tg.addHandler(BotLogsHandler(bot, chat_id))
    logger_tg.info('QUIZ_Bot TG is running')

    try:
        updater.start_polling()
        updater.idle()
    except Exception as error:
        logger_tg.error(f'Возникла ошибка в работе бота: {error}')