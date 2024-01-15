FROM ubuntu:22.04
LABEL authors="srg.markov"
LABEL description="QUIZ bot for vk and tg"
RUN apt-get update
RUN apt install python3 -y
RUN apt install python3-pip -y
RUN mkdir -p /opt/app/
COPY requirements.txt /opt/app/requirements.txt

WORKDIR /opt/app
RUN pip3 install -r requirements.txt

COPY tg_quiz_bot.py .
COPY vk_quiz_bot.py .
COPY runscript.sh .
COPY questions.py .

CMD ["bash","runscript.sh"]