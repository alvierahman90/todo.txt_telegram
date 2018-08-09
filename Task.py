from re import match
from datetime import datetime as d


class Task:
    def __init__(self, text):
        # defaults
        self.completion_date = None
        self.creation_date = None
        # for sorting, lower than all alphabet letters
        self.priority = "{"
        self.done = False
        self.projects = []
        self.contexts = []
        self.specials = []

        arguments = text.split(' ')
        counter = 0
        if arguments[counter] == 'x':
            self.done = True
            counter += 1

        # try to get priority
        priorities = match("\\([a-zA-Z]\\)", arguments[counter])
        if priorities is not None:
            self.priority = arguments[counter].split('(')[1].split(')')[0]
            self.priority = self.priority.upper()
            counter += 1

        # try to get completion date if done

        if self.done:
            try:
                self.completion_date = d.strptime(arguments[counter],
                                                  '%Y-%m-%d')
                counter += 1
            except ValueError as e:
                pass

        # try to get creation date
        try:
            self.creation_date = d.strptime(arguments[counter], '%Y-%m-%d')
            counter += 1
        except ValueError as e:
            pass

        # you cannot have a completion date w/o a creation date
        if self.creation_date is None and self.completion_date is not None:
            self.creation_date = self.completion_date
            self.completion_date = None

        # auto mark tasks with completion date as done
        if self.completion_date is not None:
            self.done = True

        self.body = " ".join(arguments[counter:])

        # the rest of the arguments may have projects, contexts, specials
        for i in arguments[counter:]:
            if len(i) < 1:
                continue
            if i[0] == '+':
                self.projects.append(i.split('+')[1])
            elif i[0] == '-':
                self.contexts.append(i.split('-')[1])
            elif ':' in i:
                arguments = i.split(':')
                key = arguments[0]
                value = ":".join(arguments[1:])
                special = {key: value}
                self.specials.append(special)

    def do(self):
        if self.done:
            return
        self.done = True

    def undo(self):
        if not self.done:
            return

        self.done = False

    def __str__(self):
        text = ""

        if self.done:
            text += "x "

        if self.priority != '{':
            text += '(' + self.priority + ') '

        if self.completion_date:
            text += str(self.completion_date).split(' ')[0] + ' '

        if self.creation_date:
            text += str(self.creation_date).split(' ')[0] + ' '

        text += self.body

        return text
