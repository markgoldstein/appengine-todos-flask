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
"""Todos storage.

This module defines two subclasses of ndb model that are used to implement
a to do list:
- Todo represents a single item on the list
- TodoList is a list of Todo items

The operations for managing a TodoList are:
- TodoList.get_or_create # fetch an existing TodoList, or create a new one.
- TodoList.add_todo      # add a new Todo item to the list.
- TodoList.update_todo   # update an existing Todo item in the list.
- TodoList.get_all_todos # get all Todo items in the list.
- TodoList.flush_todos # delete all the Todo items in the list where done==True.
"""

from google.appengine.ext import ndb


class Todo(ndb.Model):
    """Todo item model.

    A datastore entity with three properties:

    - `text`: a string up to 500 characters long that describes a todo item. The
      default is an empty string. This property is not indexed.
    - `done`: a boolean property indicating whether a task has been "checked
      off." It defaults to `False`. This property is indexed.
    - `created`: a datetime property set to the current time when the entity is
      created. This property is indexed.
    """

    text = ndb.StringProperty(default='', indexed=False)
    done = ndb.BooleanProperty(default=False)
    created = ndb.DateTimeProperty(auto_now_add=True)


class TodoList(ndb.Model):
    """Todo list model.

    A datastore entity used as the parent of one or more Todo entities to define
    an entity group. It has no properties, but like any entity, it has a unique
    key, which is treated as the name of the list.

    An entity group lets you perform consistent queries and transactional
    updates on the entities in the group.
    """

    @classmethod
    def get_or_create(cls, name):
        """Get or create a new TodoList.

        Uses the `ndb.get_or_insert()` method to transactionaly search for an
        existing TodoList whose key is the given name, and returns it if one is
        found.
        
        If there is no matching entity, creates and returns a new TodoList with
        its entity key set to `ndb.Key('TodoList', name)`. An insert mutation
        is performed to add the new list to the datastore.
        """
        return TodoList.get_or_insert(name)

    def add_todo(self, text_string):
        """Create a new Todo entity in the TodoList.

        Constructs a new Todo entity with the `text` property set to the given
        string, and its parent set to the TodoList.

        The `put()` method performs a transactional insert mutation that inserts
        the new entity into the datastore and auto-assigns it a numeric ID.

        Because all the Todos in the same TodoList have the same parent, they
        belong to the same entity group. This provides strong consistency, but
        it also limits transactional inserts to one per second.
        """

        todo = Todo(text=text_string, parent=self.key)
        todo.put()
        return todo

    def update_todo(self, todo_id, text_string, done):
        """Update an existing Todo entity in the TodoList.

        Constructs a new Todo entity with a given numeric ID, `text`, and
        `done` properties. Sets its parent to the TodoList.

        The `put()` method performs a transactional mutation to the datastore
        that updates the existing entity.

        Because all the Todos in the same TodoList have the same parent,
        they belong to the same entity group. This provides strong consistency,
        but it also limits transactional updates to one per second.
        """

        todo = Todo(id=id, text=text_string, done=done, parent=self.key)
        todo.put()
        return todo

    def get_all_todos(self):
        """Fetch all the Todo items in the TodoList ordered by creation date.

        Because the query has an ancestor filter that specifies
        the entity group containing all the Todos in the TodoList,
        it returns a strongly consistent result.
        """

        return Todo.query(ancestor=self.key).order(Todo.created).fetch()

    @ndb.transactional
    def flush_todos(self):
        """Delete all the completed Todo items, those with done==True.

        The decorator `@ndb.transactional` creates a transaction that begins
        when the method is invoked, and commits when the method exits with no
        exceptions. The transaction involves two operations:
        
        - Fetch the keys of all the Todo entities whose `done` property is `True`.
        - Batch delete the entities with those keys.

        Because the operations are performed within a transaction, and the
        TodoList that's involved is an entity group, it is guaranteed that:
        - The query has a strongly consistent view of the TodoList at the
          beginning of the transaction.
        - All write operations will succeed, as long no other update
          to the same TodoList occurs while this method is running.
        """

        keys = Todo.query(Todo.done == True,
                          ancestor=self.key).fetch(keys_only=True)
        ndb.delete_multi(keys)
