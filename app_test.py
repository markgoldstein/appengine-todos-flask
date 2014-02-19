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
import json

import os
import sys
import appengine_config
sys.path.insert(0, os.environ.get('GOOGLE_APPENGINE_SDK_PATH'))
import dev_appserver
dev_appserver.fix_sys_path()
from google.appengine.ext import testbed

import main
main.app.debug = True


class TodoAppTestCase(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub(use_sqlite=True)
        self.testbed.init_memcache_stub()
        self.app = main.app.test_client()

    def tearDown(self):
        self.testbed.deactivate()

    def testAPI(self):
        self.assertEquals(0, len(json.loads(self.app.get('/todos').data)))
        foo_todo = json.loads(self.app.post('/todos', data=json.dumps({'text':'foo'})).data)
        self.app.post('/todos', data=json.dumps({'text':'bar'}))
        self.assertEquals(2, len(json.loads(self.app.get('/todos').data)))
        self.app.put('/todos/{id}'.format(**foo_todo), data=json.dumps({'text': 'foo', 'done':True}))
        self.assertEquals(2, len(json.loads(self.app.get('/todos').data)))
        self.app.delete('/todos')
        self.assertEquals(1, len(json.loads(self.app.get('/todos').data)))

if __name__ == '__main__':
    unittest.main()
