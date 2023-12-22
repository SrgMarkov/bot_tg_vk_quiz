import os

from dotenv import load_dotenv


def format_text(text: str) -> str:
    return text.replace('\n', ' ').split(':')[1]


def get_questions():
    load_dotenv()
    questions_folder = os.getenv('QUESTIONS_FOLDER')
    questions_files = [os.path.join(questions_folder, file) for file in os.listdir(questions_folder)]
    questions_for_bot = []

    for questions_file in questions_files:
        with open(questions_file, 'r', encoding="KOI8-R") as text_file:
            encoded_text_file = text_file.read()
            questions = encoded_text_file.split('\n\n')
            for question in questions:
                if ('Вопрос' in question) \
                        and ('aud' not in question) \
                        and ('pic' not in question) \
                        and ('Ведущему' not in question):
                    item_index = questions.index(question)
                    try:
                        questions_for_bot.append({'question': format_text(question),
                                                  'answer': format_text(questions[item_index + 1])})
                    except IndexError:
                        pass
    return questions_for_bot
