import sys

if len(sys.argv) != 2 or sys.argv[1] == 'help':
    printl("USAGE: " + sys.argv[0] + " BOT_TOKEN")
    sys.exit(0)

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

import logging
import db
import pydo
from fuzzywuzzy import process as fuzzyprocess
from fuzzywuzzy import utils as fuzzyutils


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

updater = Updater(token=sys.argv[1], use_context=True)
dispatcher = updater.dispatcher

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="hiiiiiiiiii. what do you need to get done today?")

dispatcher.add_handler(CommandHandler('start', start))

def ls(update, context):
    tasks = db.get_all_user_tasks(update.effective_user)
    r = ""
    for task in tasks:
        if task.done is ('done' in update.message['text']) or ('all' in update.message['text']):
            r+= f"{task.id} {str(task)}"
            r+= '\n'

    r = r if r != "" else "no tasks!"
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=r)

dispatcher.add_handler(CommandHandler('ls', ls))

def do(update, context):
    for arg in context.args:
        if not arg.isnumeric():
            task_ids = [fuzzy_get_task_id(update.effective_user, ' '.join(context.args))]
            break
    else:
        task_ids = [int(x) for x in context.args]

    for task_id in task_ids:
        task = db.get_task(update.effective_user, task_id)
        task.do()
        db.update_task(update.effective_user, task)

    context.bot.send_message(chat_id=update.effective_chat.id, text=str(task_ids))

def fuzzy_get_task_id(user, text):
    task_strs = [str(task) for task in db.get_all_user_tasks(user)]
    return task_strs.index(fuzzyprocess.extractOne(text, task_strs)[0])

dispatcher.add_handler(CommandHandler('do', do))


def new_task(update, context):
    db.add_task(update.effective_user, pydo.Task(update.message.text))
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Created task: {update.message.text}")

dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), new_task))

updater.start_polling()
