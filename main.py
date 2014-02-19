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
"""Todo Flask backend demo.

This is a sample Flask JSON backend for a todo app.

It support the following methods:
- Create a new todo
POST /todos
> {"text": "do this"}
201 /todos/1
< {"id": 1, "text": "do this", "created": 1356724843.0, "done": false}
- Update an existing todo
PUT /todos/1
> {"id": 1, "text": "do this", "created": 1356724843.0, "done": true}
< {"id": 1, "text": "do this", "created": 1356724843.0, "done": true}
- List existing todos:
GET /todos
>
< [{"id": 1, "text": "do this", "created": 1356724843.0, "done": true},
   {"id": 2, "text": "do that", "created": 1356724849.0, "done": false}]
- Delete 'done' todos:
DELETE /todos
>
< [2]
"""
import json
from flask import Flask, request, abort

from todos import TodoList, Todo

app = Flask(__name__)
todo_list_name = 'default'

class TodoEncoder(json.JSONEncoder):
    """Todo item JSON encoder."""
    def default(self, obj):
        if isinstance(obj, Todo):
            return {
                'id': obj.key.id(),
                'text': obj.text,
                'done': obj.done,
                'created': obj.created.isoformat()
            }
        return json.JSONEncoder.default(self, obj)

@app.route('/todos', methods=['GET'])
def get_todos():
    todo_list = TodoList.get_or_create(todo_list_name)
    return json.dumps(todo_list.get_all_todos(), cls=TodoEncoder)

@app.route('/todos', methods=['POST'])
def add_todo():
    todo_list = TodoList.get_or_create(todo_list_name)
    kwargs = json.loads(request.data)
    return json.dumps(todo_list.add_todo(**kwargs), cls=TodoEncoder)

@app.route('/todos/<int:id>', methods=['PUT'])
def update_todo(id):
    todo_list = TodoList.get_or_create(todo_list_name)
    kwargs = json.loads(request.data)
    return json.dumps(todo_list.update_todo(id, **kwargs), cls=TodoEncoder)

@app.route('/todos', methods=['DELETE'])
def archive_todos():
    todo_list = TodoList.get_or_create(todo_list_name)
    return json.dumps(todo_list.archive_todos())
