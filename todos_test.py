#! /usr/bin/env python
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import unittest

import os
import sys
import appengine_config
sys.path.insert(0, os.environ.get('GOOGLE_APPENGINE_SDK_PATH'))
import dev_appserver
dev_appserver.fix_sys_path()
from google.appengine.ext import testbed

from todos import TodoList


class TodosTestCase(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub(use_sqlite=True)
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def testTodoListGetAll(self):
        todo_list = TodoList.get_or_create('list1')
        todo_list.add_todo(text='foo')
        todo_list.add_todo(text='bar')
        self.assertEquals(2, len(todo_list.get_all_todos()))

    def testTodoListArchive(self):
        todo_list = TodoList.get_or_create('list2')
        todo_list.add_todo(text='foo')
        todo = todo_list.add_todo(text='bar')
        todo_list.update_todo(id=todo.key.id(),
                              text='bar', done=True)
        todo_list.archive_todos()
        todos = todo_list.get_all_todos()
        self.assertEquals(1, len(todos))
        self.assertEquals(False, todos[0].done)

if __name__ == '__main__':
    unittest.main()
