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



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

updater = Updater(token=sys.argv[1], use_context=True)
dispatcher = updater.dispatcher


def new_task(update, context):
    db.add_task(update.effective_user, pydo.Task(update.message.text))
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"created task: {update.message.text}")


def delete(update, context):
    task_ids = db.get_task_ids_from_context(update.effective_user, context)

    for task_id in task_ids:
        task = db.remove_task_by_id(update.effective_user, task_id)

        if task is None:
            context.bot.send_message(chat_id=update.effective_chat.id,
                    text="task not found :("
            )
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"deleted task: {task}")


def do(update, context):
    task_ids = db.get_task_ids_from_context(update.effective_user, context)

    for task_id in task_ids:
        task = db.get_task(update.effective_user, task_id)
        task.do()
        db.update_task(update.effective_user, task)

    for id in task_ids:
        context.bot.send_message(chat_id=update.effective_chat.id,
                text='completed task: ' + str(db.get_task(update.effective_user, id))
        )


def ls(update, context):
    tasks = db.get_all_user_tasks(update.effective_user)
    r = ""
    for task in tasks:
        if str(task) == "":
            continue

        if task.done is ('done' in update.message['text']) or ('all' in update.message['text']):
            r+= f"{task.id} {str(task)}"
            r+= '\n'

    r = r if r != "" else "no tasks!"
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=r)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="hiiiiiiiiii. what do you need to get done today?")


def undo(update, context):
    task_ids = db.get_task_ids_from_context(update.effective_user, context)

    for task_id in task_ids:
        task = db.get_task(update.effective_user, task_id)
        task.undo()
        db.update_task(update.effective_user, task)

    for id in task_ids:
        context.bot.send_message(chat_id=update.effective_chat.id,
                text='undone task: ' + str(db.get_task(update.effective_user, id))
        )


dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), new_task))
dispatcher.add_handler(CommandHandler('delete', delete))
dispatcher.add_handler(CommandHandler('do', do))
dispatcher.add_handler(CommandHandler('ls', ls))
dispatcher.add_handler(CommandHandler('rm', delete))
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('undo', undo))

updater.start_polling()
