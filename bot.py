#!/usr/bin/env python3

import telepot
import re
import json
import time
from Task import Task
from telepot.loop import MessageLoop


with open('config.json') as file:
    config = json.loads(file.read())

bot = telepot.Bot(config['token'])


def on_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type != 'text':
        bot.sendMessage(chat_id, "Not a text command")
        return
    text = msg['text']

    command = text.split(' ')[0].lower()
    arguments = text.split(' ')[1:]

    if command in '/add':
        add_task(Task(" ".join(arguments)), chat_id)
    elif command == '/rm':
        rm_tasks(arguments, chat_id)
    elif command == '/ls':
        ls_tasks(arguments, chat_id)
    elif command == '/do':
        do_tasks(arguments, chat_id)
    elif command == '/undo':
        undo_tasks(arguments, chat_id)
    else:
        add_task(Task(text), chat_id)


def add_task(task, chat_id):
    tasks = get_tasks(chat_id)
    tasks.append(task)
    set_tasks(tasks, chat_id)


def rm_task(task, chat_id):
    tasks = get_tasks(chat_id)
    tasks.remove(task)
    set_tasks(tasks)


def rm_tasks(tasks, chat_id):
    for i in tasks:
        rm_task(i, chat_id)


def get_tasks(chat_id):
    with open(config['tasks_file']) as file:
        tasks_dict = json.loads(file.read())

    if chat_id is None:
        return tasks_dict

    chat_id = str(chat_id)

    if chat_id not in tasks_dict:
        tasks_dict[chat_id] = ""

    tasks = []
    for i in tasks_dict[chat_id].split('\n'):
        tasks.append(Task(i))

    return tasks


def get_task(task_id, chat_id):
    return get_tasks(chat_id)[task_id]


def set_tasks(tasks, chat_id):
    task_dict = get_tasks(None)
    texts = []
    for i in tasks:
        texts.append(i.text)

    plaintext = "\n".join(texts)

    task_dict[chat_id] = plaintext

    with open(config['tasks_file'], 'w+') as file:
        file.write(json.dumps(task_dict))


def set_task(task_id, task, chat_id):
    tasks = get_tasks(chat_id)
    tasks[task_id] = task
    set_tasks(tasks, chat_id)


def ls_tasks(arguments, chat_id):
    tasks = get_tasks(chat_id)
    counter = 0

    for i in range(len(tasks)):
        tasks[i] = (counter, tasks[i])
        counter += 1

    tasks = sorted(tasks, key=lambda tup: tup[1].text)

    # create list of filters
    filters = []
    nfilters = []
    for i in arguments:
        if re.match("^f:", i) is not None:
            filters.append(i.split("f:")[1])
        elif re.match("^filter:", i) is not None:
            filters.append(i.split("filter:")[1])
        elif re.match("^!f:", i) is not None:
            nfilters.append(i.split("!f:")[1])
        elif re.match("^!filter:", i) is not None:
            nfilters.append(i.split("!filter:")[1])

    text = "Tasks:\n"
    for i in tasks:
        task = i[1]
        counter += 1
        filter_pass = True

        # hidden texts
        if task.done and ":show-hidden" not in arguments:
            continue
        if task.done and ":only-hidden" in arguments:
            continue

        # filter checking
        for ii in filters:
            filter_pass = ii in task.text

        # needs continue statement after each filter list
        if not filter_pass:
            continue

        for ii in nfilters:
            filter_pass = ii not in task.text

        if not filter_pass:
            continue

        text += str(i[0]) + " " + i[1].text + "\n"

    bot.sendMessage(chat_id, text)


def do_tasks(task_ids, chat_id):
    for i in task_ids:
        task = get_task(int(i), chat_id)
        task.do()
        set_task(int(i), task, chat_id)


def undo_tasks(task_ids, chat_id):
    for i in task_ids:
        task = get_task(int(i), chat_id)
        task.undo()
        set_task(int(i), task, chat_id)


MessageLoop(bot, on_message).run_as_thread()

while True:
    time.sleep(5)
