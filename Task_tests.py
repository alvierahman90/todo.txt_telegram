#!/usr/bin/env python3

import unittest
import datetime
from Task import Task as T


class TaskTestCase(unittest.TestCase):
    def test_basic(self):
        text = "task"
        task = T(text)
        self.assertEqual(str(task), text)
        self.assertEqual(task.done, False)
        self.assertEqual(task.priority, '{')
        self.assertEqual(task.completion_date, None)
        self.assertEqual(task.creation_date, None)
        self.assertEqual(task.projects, [])
        self.assertEqual(task.contexts, [])
        self.assertEqual(task.specials, [])

    def test_basic_done(self):
        text = "x basic test task"
        task = T(text)
        self.assertEqual(str(task), text)
        self.assertEqual(task.done, True)
        self.assertEqual(task.priority, '{')
        self.assertEqual(task.completion_date, None)
        self.assertEqual(task.creation_date, None)
        self.assertEqual(task.projects, [])
        self.assertEqual(task.contexts, [])
        self.assertEqual(task.specials, [])

    def test_prioritized(self):
        text = "(A) prioritized test task"
        task = T(text)
        self.assertEqual(str(task), text)
        self.assertEqual(task.done, False)
        self.assertEqual(task.priority, 'A')
        self.assertEqual(task.completion_date, None)
        self.assertEqual(task.creation_date, None)
        self.assertEqual(task.projects, [])
        self.assertEqual(task.contexts, [])
        self.assertEqual(task.specials, [])

    def test_prioritized_ignore_incorrect(self):
        text = "(AA) prioritized test task"
        task = T(text)
        self.assertEqual(str(task), text)
        self.assertEqual(task.done, False)
        self.assertEqual(task.priority, '{')
        self.assertEqual(task.completion_date, None)
        self.assertEqual(task.creation_date, None)
        self.assertEqual(task.projects, [])
        self.assertEqual(task.contexts, [])
        self.assertEqual(task.specials, [])

    def test_prioritized_done(self):
        text = "x (A) prioritized test task"
        task = T(text)
        self.assertEqual(str(task), text)
        self.assertEqual(task.done, True)
        self.assertEqual(task.priority, 'A')
        self.assertEqual(task.completion_date, None)
        self.assertEqual(task.creation_date, None)
        self.assertEqual(task.projects, [])
        self.assertEqual(task.contexts, [])
        self.assertEqual(task.specials, [])

    def test_with_creation_date(self):
        text = "2018-06-24 test task"
        task = T(text)
        self.assertEqual(str(task), text)
        self.assertEqual(task.done, False)
        self.assertEqual(task.priority, '{')
        self.assertEqual(task.completion_date, None)
        self.assertEqual(task.creation_date,
                         datetime.datetime(2018, 6, 24, 0, 0))
        self.assertEqual(task.projects, [])
        self.assertEqual(task.contexts, [])
        self.assertEqual(task.specials, [])

    def test_with_creation_and_completion_date(self):
        text = "x 2018-06-24 2018-05-24 test task"
        task = T(text)
        self.assertEqual(str(task), text)
        self.assertEqual(task.done, True)
        self.assertEqual(task.priority, '{')
        self.assertEqual(task.completion_date,
                         datetime.datetime(2018, 6, 24, 0, 0))
        self.assertEqual(task.creation_date,
                         datetime.datetime(2018, 5, 24, 0, 0))
        self.assertEqual(task.projects, [])
        self.assertEqual(task.contexts, [])
        self.assertEqual(task.specials, [])

    def test_with_creation_and_completion_and_priority_date(self):
        text = "x (B) 2018-06-24 2018-05-24 test task"
        task = T(text)
        self.assertEqual(str(task), text)
        self.assertEqual(task.done, True)
        self.assertEqual(task.priority, 'B')
        self.assertEqual(task.completion_date,
                         datetime.datetime(2018, 6, 24, 0, 0))
        self.assertEqual(task.creation_date,
                         datetime.datetime(2018, 5, 24, 0, 0))
        self.assertEqual(task.projects, [])
        self.assertEqual(task.contexts, [])
        self.assertEqual(task.specials, [])

    def test_special(self):
        text = "special task special:value"
        task = T(text)
        self.assertEqual(str(task), text)
        self.assertEqual(task.done, False)
        self.assertEqual(task.priority, '{')
        self.assertEqual(task.completion_date, None)
        self.assertEqual(task.creation_date, None)
        self.assertEqual(task.projects, [])
        self.assertEqual(task.contexts, [])
        self.assertEqual(task.specials, [{"special": "value"}])

    def test_specials_with_colons(self):
        text = "give muffin her pen back due:2028-07-10T14:28:15Z+0100"
        task = T(text)
        self.assertEqual(str(task), text)
        self.assertEqual(task.done, False)
        self.assertEqual(task.priority, '{')
        self.assertEqual(task.completion_date, None)
        self.assertEqual(task.creation_date, None)
        self.assertEqual(task.projects, [])
        self.assertEqual(task.contexts, [])
        self.assertEqual(task.specials, [{"due": "2028-07-10T14:28:15Z+0100"}])

    def test_standardized_priority_case(self):
        text = "(a) standard prioritization test"
        text_standardized_priority = "(A) standard prioritization test"
        task = T(text)
        self.assertEqual(str(task), text_standardized_priority)
        self.assertEqual(task.done, False)
        self.assertEqual(task.priority, 'A')
        self.assertEqual(task.completion_date, None)
        self.assertEqual(task.creation_date, None)
        self.assertEqual(task.projects, [])
        self.assertEqual(task.contexts, [])
        self.assertEqual(task.specials, [])


unittest.main()
