import pydo
import telegram
import redis

from fuzzywuzzy import process as fuzzyprocess
from fuzzywuzzy import utils as fuzzyutils

def _redis_user_tasks_key(user_id):
    return f'user_tasks:{user_id}'

r = redis.Redis(host='localhost', port=6379,
        charset='utf-8', decode_responses=True)

def get_all_user_tasks(user) -> "list of pydo.Task":
    global r
    task_list = r.lrange(_redis_user_tasks_key(user.id), 0, -1)
    response = []

    for id, task_str in enumerate(task_list):
        task = pydo.Task(task_str)
        task.id = id
        response.append(task)

    return response

def export_user_tasks(user: telegram.User) -> str:
    return '\n'.join(r.lrange(_redis_user_tasks_key(user.id)), 0, -1)

def get_task(user: telegram.User, task_id: int) -> pydo.Task:
    for task in get_all_user_tasks(user):
        if int(task.id) == int(task_id):
            return task

def fuzzy_get_task_id(user, text):
    task_strs = [str(task) for task in get_all_user_tasks(user)]
    return task_strs.index(fuzzyprocess.extractOne(text, task_strs)[0])

def get_task_ids_from_context(user, context):
    for arg in context.args:
        if not arg.isnumeric():
            task_ids = [fuzzy_get_task_id(user, ' '.join(context.args))]
            break
    else:
        task_ids = [int(x) for x in context.args]

    return task_ids

def add_task(user: telegram.User, task: pydo.Task) -> pydo.Task:
    r.rpush(_redis_user_tasks_key(user.id), str(task))
    return task

def update_task(user: telegram.User, new_task: pydo.Task) -> pydo.Task:
    r.lset(_redis_user_tasks_key(user.id), new_task.id, str(new_task))
    return new_task

def remove_task_by_id(user: telegram.User, task_id: int) -> int:
    # instead of removing an item, set it's text value to nothing, so that all other tasks' ids
    # don't change
    task = get_task(user, task_id)
    if task is not None:
        update_task(user, pydo.Task("", id=task_id))

    return task

def remove_task(user: telegram.User, task: pydo.Task) -> pydo.Task:
    return remove_task_by_id(user.id, task.id)
