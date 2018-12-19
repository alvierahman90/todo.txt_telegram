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
from pydo import Task

VERSION = "v1.2.1"


PROPERTY_LAST_COMMAND = "last_command"
PROPERTY_LAST_ARGUMENTS = "last_arguments"

CONFIG_FILE = '/config/config.json'
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
TASKS_FILE = "/config/tasks.json"


with open(CONFIG_FILE) as file:
    CONFIG = json.loads(file.read())

BOT = telepot.Bot(CONFIG['token'])


def on_message(msg):
    """
    The function which is run when MessageLoop receives an event
    :param msg: The message object, passed by MessageLoop
    """
    content_type, chat_type, chat_id = telepot.glance(msg)

    if content_type != 'text':
        BOT.sendMessage(chat_id, "I can only understand text, sorry.")
        return
    text = msg['text']

    command = text.split(' ')[0]
    arguments = text.split(' ')[1:]

    if command == '/last':
        last_checks(chat_id)
        command = get_property(chat_id, PROPERTY_LAST_COMMAND)
        arguments = get_property(chat_id, PROPERTY_LAST_ARGUMENTS)
    else:
        set_property(chat_id, PROPERTY_LAST_COMMAND, command)
        set_property(chat_id, PROPERTY_LAST_ARGUMENTS, arguments)

    process_command(chat_id, command, arguments)


def process_command(chat_id, command, arguments):
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
        add_task(chat_id, Task(" ".join(arguments)))
    elif command == '/rm':
        function_fuzzy_checker(chat_id, arguments, rm_tasks)
    elif command == '/ls':
        ls_tasks(chat_id, arguments)
    elif command == '/do':
        # do_tasks(chat_id, arguments)
        function_fuzzy_checker(chat_id, arguments, do_tasks)
    elif command == '/undo':
        # undo_tasks(chat_id, arguments)
        function_fuzzy_checker(chat_id, arguments, undo_tasks)
    elif command == '/export':
        export_tasks(chat_id)
    elif command == '/marco':
        marco(chat_id)
    elif command == '/delete_all_tasks':
        delete_all_tasks(chat_id)
    elif command == '/priority':
        #priority(chat_id, arguments)
        function_fuzzy_checker(chat_id, arguments, priority, ignore=[0],
                               handler=fuzzy_priority_handler)
    else:
        set_property(chat_id, PROPERTY_LAST_COMMAND, '/add')
        set_property(chat_id, PROPERTY_LAST_ARGUMENTS, arguments)

        # command has to prefixed here since there is no actual command with a
        # preceding slash
        add_task(chat_id, Task(command + " " + " ".join(arguments)))


def add_task(chat_id, task):
    """
    Adds a task
    :param task: A Task object
    :param chat_id: A numerical telegram chat_id
    """
    tasks = get_tasks(chat_id)
    tasks.append(task)
    set_tasks(chat_id, tasks)
    BOT.sendMessage(chat_id, "Added task: {0}".format(task))


def rm_tasks(chat_id, task_ids):
    """
    Delete multiple tasks
    :param task_ids: An iterable of IDs of task objects
    :param chat_id: A numerical telegram chat_id
    """
    tasks = get_tasks(chat_id)
    for i in task_ids:
        if not is_task_id_valid(chat_id, i):
            continue
        set_tasks(chat_id, [x for x in tasks if str(tasks[int(i)]) != str(x)])
        BOT.sendMessage(chat_id, "Removed task: {0}".format(tasks[int(i)]))


def get_property(chat_id, property_name):
    """
    // TODO figure out what this does
    :param property_name:
    :param chat_id:
    :return:
    """
    with open(TASKS_FILE) as tasks_file:
        info_dict = json.loads(tasks_file.read())

    key = property_name + ":" + str(chat_id)

    if key in info_dict.keys():
        return info_dict[key]
    return None


def set_property(chat_id, property_name, value):
    """
    // TODO figure out what this does
    :param property_name:
    :param value:
    :param chat_id:
    """
    with open(TASKS_FILE) as tasks_file:
        info_dict = json.loads(tasks_file.read())

    key = property_name + ":" + str(chat_id)
    info_dict[key] = value

    with open(TASKS_FILE, 'w') as tasks_file:
        info_dict = tasks_file.write(json.dumps(info_dict))


def get_tasks(chat_id, raw=False):
    """
    Returns a list of tasks
    :param chat_id: A numerical telegram chat_id, or None to get tasks for all users
    :param raw: Defaults to False, raw returns the tasks as strings
    :return: Returns a python list of tasks, or a python dict if raw is True
    """
    with open(TASKS_FILE) as tasks_file:
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


def get_task(chat_id, task_id):
    """
    Returns single task
    :param task_id: ID of task
    :param chat_id: Telegram chat_id
    :return: Task object or none if task_id is invalid
    """
    if not is_task_id_valid(chat_id, task_id):
        return None
    return get_tasks(chat_id)[int(task_id)]


def set_tasks(chat_id, tasks):
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

    with open(TASKS_FILE, 'w+') as tasks_file:
        tasks_file.write(json.dumps(task_dict))


def set_task(chat_id, task_id, task):
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
    set_tasks(chat_id, tasks)


def ls_tasks(chat_id, arguments):
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

def do_tasks(chat_id, task_ids):
    """
    Mark tasks by ID as done
    :param task_ids: Iterable of task IDs
    :param chat_id: Telegram chat_id
    """
    for i in task_ids:
        if not is_task_id_valid(chat_id, i):
            continue

        task = get_task(chat_id, int(i))
        task.do()
        set_task(chat_id, int(i), task)
        BOT.sendMessage(chat_id, "Did task {1}: {0}".format(str(task), i))


def undo_tasks(chat_id, task_ids):
    """
    Mark tasks as not done
    :param task_ids: Iterable of task IDs
    :param chat_id: Telegram chat_id
    """
    for i in task_ids:
        if not is_task_id_valid(chat_id, i):
            continue
        task = get_task(chat_id, int(i))
        task.undo()
        set_task(chat_id, int(i), task)
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
    if get_property(chat_id, PROPERTY_LAST_ARGUMENTS) is None or \
            get_property(chat_id, PROPERTY_LAST_COMMAND) is None:
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
    text += "\n[View help on GitHub](alvierahman90.github.io/todo.txt_telegram/src/help.html)"
    BOT.sendMessage(chat_id, text, parse_mode='Markdown')


def delete_all_tasks(chat_id):
    """
    Deletes all the tasks for a user. Also exports the tasks in case the user
    made a mistake.
    :param chat_id: Telegram chat id
    """
    export_tasks(chat_id)
    set_tasks(chat_id, [])
    BOT.sendMessage(chat_id, "Deleted all tasks.")


def priority(chat_id, arguments):
    """
    Changes the priority of a task
    """
    BOT.sendMessage(chat_id, repr(arguments))
    for i, argument in enumerate(arguments):
        BOT.sendMessage(chat_id, f"Argument {i}: {argument}")

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

    set_tasks(chat_id, tasks)

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
    return function(chat_id, [task_id])


def fuzzy_priority_handler(chat_id, text, function):
    """
    Sets the priority of the closest matching task to text
    :param chat_id: Telegram chat_id
    :param text: text to match to a task to perform function on it
    :param function: the function with which to process the task_id (not used)
    """
    # TODO allow fuzzy_action to run on commands with more positional arguments
    arguments = text.split(' ')
    new_priority = arguments.pop(0)
    task_id, matchness = fuzzy_get_task_id_from_text(chat_id, ' '.join(arguments))
    BOT.sendMessage(chat_id, "fprepr: " + repr([new_priority, task_id]))
    return priority(chat_id, [new_priority, task_id])

def function_fuzzy_checker(chat_id, arguments, function, ignore=[], handler=fuzzy_action):
    """
    Checks if the all arguments are numerical and if they are it runs the
    function, otherwise it runs fuzzy_action with that function.
    :param chat_id: Telegram chat_id
    :param arguments: list of arguments form process_command
    :param function: the function to be executed
    :param ignore: a list of argument indexes to ignore when checking if to run fuzzy
    :param handler: the function which executes the function in fuzzy mode
    """

    numerical = True
    for i, val in enumerate(arguments):
        if i in ignore:
            continue
        if not val.isdigit():
            numerical = False
            break

    if not numerical:
        handler(chat_id, ' '.join(arguments), function)
    else:
        function(chat_id, arguments)


if __name__ == "__main__":
    MessageLoop(BOT, on_message).run_as_thread()

    while True:
        time.sleep(1)
