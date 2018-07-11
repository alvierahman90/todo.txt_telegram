#!/usr/bin/env python3

import unittest
import datetime
from Task import Task as T


class TaskTestCase(unittest.TestCase):
    def test_basic(self):
        task = T("task")
        self.assertEqual(task.done, False)
        self.assertEqual(task.priority, '{')
        self.assertEqual(task.completion_date, None)
        self.assertEqual(task.creation_date, None)
        self.assertEqual(task.projects, [])
        self.assertEqual(task.contexts, [])
        self.assertEqual(task.specials, [])

    def test_basic_done(self):
        task = T("x basic test task")
        self.assertEqual(task.done, True)
        self.assertEqual(task.priority, '{')
        self.assertEqual(task.completion_date, None)
        self.assertEqual(task.creation_date, None)
        self.assertEqual(task.projects, [])
        self.assertEqual(task.contexts, [])
        self.assertEqual(task.specials, [])

    def test_prioritized(self):
        task = T("(A) prioritized test task")
        self.assertEqual(task.done, False)
        self.assertEqual(task.priority, 'A')
        self.assertEqual(task.completion_date, None)
        self.assertEqual(task.creation_date, None)
        self.assertEqual(task.projects, [])
        self.assertEqual(task.contexts, [])
        self.assertEqual(task.specials, [])

    def test_prioritized_ignore_incorrect(self):
        task = T("(AA) prioritized test task")
        self.assertEqual(task.done, False)
        self.assertEqual(task.priority, '{')
        self.assertEqual(task.completion_date, None)
        self.assertEqual(task.creation_date, None)
        self.assertEqual(task.projects, [])
        self.assertEqual(task.contexts, [])
        self.assertEqual(task.specials, [])

    def test_prioritized_done(self):
        task = T("x (A) prioritized test task")
        self.assertEqual(task.done, True)
        self.assertEqual(task.priority, 'A')
        self.assertEqual(task.completion_date, None)
        self.assertEqual(task.creation_date, None)
        self.assertEqual(task.projects, [])
        self.assertEqual(task.contexts, [])
        self.assertEqual(task.specials, [])

    def test_with_creation_date(self):
        task = T("2018-06-24 test task")
        self.assertEqual(task.done, False)
        self.assertEqual(task.priority, '{')
        self.assertEqual(task.completion_date, None)
        self.assertEqual(task.creation_date,
                         datetime.datetime(2018, 6, 24, 0, 0))
        self.assertEqual(task.projects, [])
        self.assertEqual(task.contexts, [])
        self.assertEqual(task.specials, [])

    def test_with_creation_and_completion_date(self):
        task = T("x 2018-06-24 2018-05-24 test task")
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
        task = T("x (B) 2018-06-24 2018-05-24 test task")
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
        task = T("special task special:value")
        self.assertEqual(task.done, False)
        self.assertEqual(task.priority, '{')
        self.assertEqual(task.completion_date, None)
        self.assertEqual(task.creation_date, None)
        self.assertEqual(task.projects, [])
        self.assertEqual(task.contexts, [])
        self.assertEqual(task.specials, [{"special": "value"}])

    def test_specials_with_colons(self):
        task = T("give muffin her pen back due:2028-07-10T14:28:15Z+0100")
        self.assertEqual(task.done, False)
        self.assertEqual(task.priority, '{')
        self.assertEqual(task.completion_date, None)
        self.assertEqual(task.creation_date, None)
        self.assertEqual(task.projects, [])
        self.assertEqual(task.contexts, [])
        self.assertEqual(task.specials, [{"due": "2028-07-10T14:28:15Z+0100"}])


unittest.main()
