
# this is a temporary db to get things working

import json
import pydo
import telegram

DB_FILE="./db.json"

class DbKeys:
    USER_TASKS = 'user_tasks'

def _create_db():
    db = {
            DbKeys.USER_TASKS : {}
            }
    with open(DB_FILE, "w+") as file:
        json.dump(db, file)

def _get_db():
    with open(DB_FILE) as file:
        return json.load(file)

def _set_db(db):
    with open(DB_FILE, "w") as file:
        json.dump(db, file)

def get_all_user_tasks(user) -> "list of pydo.Task":
    db = _get_db()
    task_list = db[DbKeys.USER_TASKS][str(user.id)]
    r = []

    for id, task_str in enumerate(task_list):
        task = pydo.Task(task_str)
        task.id = id
        r.append(task)

    return r

def export_user_tasks(user: telegram.User) -> str:
    db = _get_db()
    print(db)
    return '\n'.join(db[DbKeys.USER_TASKS][str(user.id)])

def get_task(user: telegram.User, task_id: int) -> pydo.Task:
    for task in get_all_user_tasks(user):
        if int(task.id) == int(task_id):
            return task

def create_user(db, user: telegram.User):
    if str(user.id) not in db[DbKeys.USER_TASKS].keys():
        db[DbKeys.USER_TASKS][str(user.id)] = []

    return db


def add_task(user: telegram.User, task: pydo.Task) -> pydo.Task:
    db = _get_db()
    db = create_user(db, user)

    db[DbKeys.USER_TASKS][str(user.id)].append(str(task))
    _set_db(db)
    return task

def update_task(user: telegram.User, new_task: pydo.Task) -> pydo.Task:
    db = _get_db()
    db[DbKeys.USER_TASKS][str(user.id)][new_task.id] = str(new_task)
    _set_db(db)
    return new_task

def remove_task(user: telegram.User, task_id: int) -> int:
    db = _get_db()
    # instead of removing an item, set it's text value to nothing, so that all other tasks' ids
    # don't change
    db[DbKeys.USER_TASKS][str(user.id)][str(task_id)] = ""
    _set_db(db)

def remove_task(user: telegram.User, task: pydo.Task) -> pydo.Task:
    remove_task(user.id, task.id)
    return task

try:
    _get_db()
except:
    _create_db()
