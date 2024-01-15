#!/bin/bash
python3 tg_quiz_bot.py &
python3 vk_quiz_bot.py &
# Wait for any process to exit
wait -n
# Exit with status of process that exited first
exit $?