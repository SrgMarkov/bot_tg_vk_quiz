import os
from pprint import pprint


def format_text(text: str) -> str:
    return text.replace('\n', '').split(':')[1]


questions_for_quiz = []
questions_files = [os.path.join('quiz-questions', file) for file in os.listdir('quiz-questions')]
for questions_file in questions_files:
    with open(questions_file, encoding="KOI8-R") as text_file:
        encoded_text_file = text_file.read()
        qlist = encoded_text_file.split('\n\n')
        for item in qlist:
            if 'Вопрос' in item:
                item_index = qlist.index(item)
                try:
                    questions_for_quiz.append({'question': format_text(item),
                                               'answer': format_text(qlist[item_index + 1])})
                except IndexError:
                    pass

pprint(questions_for_quiz)
