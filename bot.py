#!/usr/bin/env python3
#  coding=utf-8
"""
The bot script
Run this, I guess
"""

import re
import json
import time
import telepot
from telepot.loop import MessageLoop
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
from Task import Task

VERSION = "v1.1"


PROPERTY_LAST_COMMAND = "last_command"
PROPERTY_LAST_ARGUMENTS = "last_arguments"

CONFIG_FILE = 'config.json'
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


with open(CONFIG_FILE) as file:
    CONFIG = json.loads(file.read())

BOT = telepot.Bot(CONFIG['token'])


def on_message(msg):
    """
    The function which is run when MessageLoop receives an event
    :param msg: The message object, passed by MessageLoop
    """
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type != 'text':
        BOT.sendMessage(chat_id, "I can only understand text, sorry.")
        return
    text = msg['text']

    command = text.split(' ')[0]
    arguments = text.split(' ')[1:]

    if command == '/last':
        last_checks(chat_id)
        command = get_property(PROPERTY_LAST_COMMAND, chat_id)
        arguments = get_property(PROPERTY_LAST_ARGUMENTS, chat_id)
    else:
        set_property(PROPERTY_LAST_COMMAND, command, chat_id)
        set_property(PROPERTY_LAST_ARGUMENTS, arguments, chat_id)

    process_command(command, arguments, chat_id)


def process_command(command, arguments, chat_id):
    """
    Processes the command sent by user
    :param command: The command itself i.e /add
    :param arguments: Anything else after it as a python list
    :param chat_id: Telegram chat_id
    """
    if command == '/start':
        user_init(chat_id)
    elif command == '/help':
        user_help_info(chat_id)
    elif command == '/add':
        add_task(Task(" ".join(arguments)), chat_id)
    elif command == '/rm':
        rm_tasks(arguments, chat_id)
    elif command == '/ls':
        ls_tasks(arguments, chat_id)
    elif command == '/do':
        do_tasks(arguments, chat_id)
    elif command == '/undo':
        undo_tasks(arguments, chat_id)
    elif command == '/export':
        export_tasks(chat_id)
    elif command == '/marco':
        marco(chat_id)
    elif command == '/delete_all_tasks':
        delete_all_tasks(chat_id)
    elif command == '/priority':
        priority(chat_id, arguments)
    elif command == '/fdo':
        fuzzy_action(chat_id, ' '.join(arguments), do_tasks)
    elif command == '/fundo':
        fuzzy_action(chat_id, ' '.join(arguments), undo_tasks)
    elif command == '/frm':
        fuzzy_action(chat_id, ' '.join(arguments), rm_tasks)
    elif command == '/fpriority':
        fuzzy_priority(chat_id, arguments)
    else:
        set_property(PROPERTY_LAST_COMMAND, '/add', chat_id)
        set_property(PROPERTY_LAST_ARGUMENTS, arguments, chat_id)

        # command has to prefixed here since there is no actual command with a
        # preceding slash
        add_task(Task(command + " " + " ".join(arguments)), chat_id)


def add_task(task, chat_id):
    """
    Adds a task
    :param task: A Task object
    :param chat_id: A numerical telegram chat_id
    """
    tasks = get_tasks(chat_id)
    tasks.append(task)
    set_tasks(tasks, chat_id)
    BOT.sendMessage(chat_id, "Added task: {0}".format(task))


def rm_task(task, chat_id):
    """
    Deletes a task
    :param task: A Task object
    :param chat_id: A numerical telegram chat_id
    """
    tasks = get_tasks(chat_id)
    set_tasks([x for x in tasks if str(task) != str(x)], chat_id)
    BOT.sendMessage(chat_id, "Removed task: {0}".format(task))


def rm_tasks(task_ids, chat_id):
    """
    Delete multiple tasks
    :param task_ids: An iterable of IDs of task objects
    :param chat_id: A numerical telegram chat_id
    """
    tasks = get_tasks(chat_id)
    for i in task_ids:
        if not is_task_id_valid(chat_id, i):
            continue
        rm_task(tasks[int(i)], chat_id)


def get_property(property_name, chat_id):
    """
    // TODO figure out what this does
    :param property_name:
    :param chat_id:
    :return:
    """
    with open(CONFIG['tasks_file']) as tasks_file:
        info_dict = json.loads(tasks_file.read())

    key = property_name + ":" + str(chat_id)

    if key in info_dict.keys():
        return info_dict[key]
    return None


def set_property(property_name, value, chat_id):
    """
    // TODO figure out what this does
    :param property_name:
    :param value:
    :param chat_id:
    """
    with open(CONFIG['tasks_file']) as tasks_file:
        info_dict = json.loads(tasks_file.read())

    key = property_name + ":" + str(chat_id)
    info_dict[key] = value

    with open(CONFIG['tasks_file'], 'w') as tasks_file:
        info_dict = tasks_file.write(json.dumps(info_dict))


def get_tasks(chat_id, raw=False):
    """
    Returns a list of tasks
    :param chat_id: A numerical telegram chat_id, or None to get tasks for all users
    :param raw: Defaults to False, raw returns the tasks as strings
    :return: Returns a python list of tasks, or a python dict if raw is True
    """
    with open(CONFIG['tasks_file']) as tasks_file:
        tasks_dict = json.loads(tasks_file.read())

    if chat_id is None:
        return tasks_dict

    chat_id = str(chat_id)

    if chat_id not in tasks_dict:
        tasks_dict[chat_id] = ""

    if raw:
        return tasks_dict[chat_id]

    tasks = []
    # even if the string is empty, split will return a list of one, which
    # which creates a task that doesn't exist and without any content when user
    # has no tasks
    if tasks_dict[chat_id] == "":
        return tasks

    for i in tasks_dict[chat_id].split('\n'):
        tasks.append(Task(i))

    return tasks


def get_task(task_id, chat_id):
    """
    Returns single task
    :param task_id: ID of task
    :param chat_id: Telegram chat_id
    :return: Task object or none if task_id is invalid
    """
    if not is_task_id_valid(chat_id, task_id):
        return None
    return get_tasks(chat_id)[int(task_id)]


def set_tasks(tasks, chat_id):
    """
    Overwrite the existing tasks with a new list
    :param tasks: Iterable of Task objects
    :param chat_id: Telegram chat_id
    """
    task_dict = get_tasks(None)
    texts = []
    for i in tasks:
        texts.append(str(i))

    plaintext = "\n".join(texts)

    task_dict[chat_id] = plaintext

    with open(CONFIG['tasks_file'], 'w+') as tasks_file:
        tasks_file.write(json.dumps(task_dict))


def set_task(task_id, task, chat_id):
    """
    Overwrite a single task by ID
    :param task_id: ID of the task
    :param task: Task object itself
    :param chat_id: Telegram chat_id
    """
    if not is_task_id_valid(chat_id, task_id):
        return
    tasks = get_tasks(chat_id)
    tasks[task_id] = task
    set_tasks(tasks, chat_id)


def ls_tasks(arguments, chat_id):
    """
    Send a list of tasks to user
    :param arguments: Iterable of strings
    :param chat_id: Telegram chat_id
    """
    tasks = get_tasks(chat_id)
    if len(tasks) < 1:
        BOT.sendMessage(chat_id, "You have no tasks.")
        return
    counter = 0

    for i, value in enumerate(tasks, start=0):
        tasks[i] = (counter, value)
        counter += 1

    tasks = sorted(tasks, key=lambda tup: tup[1].priority)

    # create list of filters
    filters = []
    nfilters = [] # inverse filter
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

        if not task.done and ":only-done" in arguments:
            continue
        elif task.done and ":only-done" in arguments:
            pass
        elif task.done and ":show-done" not in arguments:
            continue

        # filter checking
        for j in filters:
            if j not in str(task):
                filter_pass = False
                break

        # needs continue statement after each filter list as filter_pass
        # gets reset
        if not filter_pass:
            continue

        for j in nfilters:
            if j in str(task):
                filter_pass = False
                break

        if not filter_pass:
            continue

        text += str(i[0]) + " " + str(i[1]) + "\n"

    BOT.sendMessage(chat_id, text)

def do_tasks(task_ids, chat_id):
    """
    Mark tasks by ID as done
    :param task_ids: Iterable of task IDs
    :param chat_id: Telegram chat_id
    """
    for i in task_ids:
        if not is_task_id_valid(chat_id, i):
            continue

        task = get_task(int(i), chat_id)
        task.do()
        set_task(int(i), task, chat_id)
        BOT.sendMessage(chat_id, "Did task {1}: {0}".format(str(task), i))


def undo_tasks(task_ids, chat_id):
    """
    Mark tasks as not done
    :param task_ids: Iterable of task IDs
    :param chat_id: Telegram chat_id
    """
    for i in task_ids:
        if not is_task_id_valid(chat_id, i):
            continue
        task = get_task(int(i), chat_id)
        task.undo()
        set_task(int(i), task, chat_id)
        BOT.sendMessage(chat_id, "Undid task {1}: {0}".format(str(task), i))


def export_tasks(chat_id):
    """
    Send all tasks to user as standard todo.txt format, to use in other apps
    :param chat_id: Telegram chat_id
    """
    text = get_tasks(chat_id, raw=True)
    if text == "":
        BOT.sendMessage(chat_id, "No tasks.")
        return

    BOT.sendMessage(chat_id, "RAW:")
    BOT.sendMessage(chat_id, text)


def marco(chat_id):
    """
    Sends the message "Polo" to user, tests if the bot is up
    :param chat_id: Telegram chat_id
    """
    BOT.sendMessage(chat_id, "Polo")


def last_checks(chat_id):
    """
    Checks if the user has sent a command already
    :param chat_id: Telegram chat_id
    """
    if get_property(PROPERTY_LAST_ARGUMENTS, chat_id) is None or \
            get_property(PROPERTY_LAST_COMMAND, chat_id) is None:
        BOT.sendMessage(chat_id, "No recorded last command")

def user_init(chat_id):
    """
    The function which is run to set up a new user
    :param chat_id: Telegram chat_id
    """
    BOT.sendMessage(chat_id, "Welcome to todo.txt but as a Telegram bot. Run"
                             " /help to get started")

def user_help_info(chat_id):
    """
    The help text sent to user
    :param chat_id: Telegram chat_id
    """
    with open('help.md') as help_file:
        text = help_file.read()
    text += "\ntodo.txt bot for Telegram version {0}".format(VERSION)
    text += "\n[View help on GitHub](alvierahman90.github.io/todo.txt_telegram/help.html)"
    BOT.sendMessage(chat_id, text, parse_mode='Markdown')


def delete_all_tasks(chat_id):
    """
    Deletes all the tasks for a user. Also exports the tasks in case the user
    made a mistake.
    :param chat_id: Telegram chat id
    """
    export_tasks(chat_id)
    set_tasks([], chat_id)
    BOT.sendMessage(chat_id, "Deleted all tasks.")


def priority(chat_id, arguments):
    """
    Changes the priority of a task
    """
    if len(arguments) < 2:
        BOT.sendMessage(chat_id, "Not enough arguments: /priority PRIORITY"
                                 "ID-OF-TASK [ID-OF-TASK...]")
        return

    priorities = list(ALPHABET)
    priorities.append('NONE')

    if arguments[0].upper() not in priorities:
        BOT.sendMessage(chat_id, "Priority (first argument) must be letter or"
                                 "'none'")
        return

    new_priority = arguments[0].upper()
    # This is what no priority is defined as for the sorting
    if new_priority == 'NONE':
        new_priority = '{'
    del arguments[0]

    tasks = get_tasks(chat_id)

    for i in arguments:
        if not is_task_id_valid(chat_id, i):
            continue

        i = int(i)
        BOT.sendMessage(chat_id, "Setting priority of '{}'.".format(tasks[i]))
        tasks[i].priority = new_priority

    set_tasks(tasks, chat_id)

    return

def is_task_id_valid(chat_id, task_id):
    """
    Checks if task_id provided is an integer and in the list
    :param chat_id: Telegram chat id
    :param task_id: ID of the task to check
    :return: the task_id as integer if valid, otherwise False
    """
    def fail():
        """
        Prints failure message
        """
        BOT.sendMessage(chat_id, "Invalid task ID '{0}' - IDs are "
                                 "integers and must actually exist (run /ls)"
                                 "".format(str(task_id)))
        return False

    if isinstance(task_id, int):
        real_task_id = int(task_id)
    elif isinstance(task_id, str):
        if task_id.isnumeric():
            real_task_id = int(task_id)
        else:
            return fail()
    else:
        return fail()

    print(real_task_id)
    print(len(get_tasks(chat_id)))
    if real_task_id < len(get_tasks(chat_id)):
        return real_task_id
    return fail()

def fuzzy_get_task_id_from_text(chat_id, text):
    """
    Fuzzy searches for the closest match to the text string given
    :param chat_id: Telegram chat_id
    :param text: The string to fuzzy match
    :return: task_id, matchness, task_text as a tuple
    """

    tasks = [str(x) for x in get_tasks(chat_id)]
    task_text, matchness = process.extractOne(text, tasks,
                                              scorer=fuzz.token_sort_ratio)
    task_id = tasks.index(task_text)
    return task_id, matchness

def fuzzy_action(chat_id, text, function):
    """
    Marks the task most similar to `text` as done
    :param chat_id: Telegram chat_id
    :param text: text to match to a task to perform function on it
    :param function: the function with which to process the task_id
    """
    task_id, matchness = fuzzy_get_task_id_from_text(chat_id, text)
    return function([task_id], chat_id)


def fuzzy_priority(chat_id, arguments):
    """
    Sets the priority of the closest matching task to text
    :param chat_id: Telegram chat_id
    :param text: text to match to a task to perform function on it
    :param function: the function with which to process the task_id
    """
    text = ' '.join(arguments[1:])
    task_id, matchness = fuzzy_get_task_id_from_text(chat_id, text)
    return priority(chat_id, [arguments[0], task_id])


if __name__ == "__main__":
    MessageLoop(BOT, on_message).run_as_thread()

    while True:
        time.sleep(1)
