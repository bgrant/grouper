# Grouper

Grouper is a Flask-based web service with a JSON/REST API that manages users
and groups.


## Dependencies

Check out `requirements.txt` to find the current list of dependencies.


## Quickstart

If you have the dependencies installed, you can run the service with

    $ python grouper.py runserver

which will start a development server at `localhost:5000`.

You can then use the JSON/REST API from a client of your choice, for example:

    $ curl -i http://localhost:5000/grouper/api/v1/users
    $ curl -i http://localhost:5000/grouper/api/v1/groups

You can also run a set of system tests by running `pytest` in this directory
after staring the server.


## JSON/REST API

Base URI: `http://localhost:5000/grouper/api/v1`

### `users` resource

 Method  | URI                      | Action
---------|--------------------------|-----------------------
GET      | [BASE]/users             | Retrieve list of users
GET      | [BASE]/users/[userid]    | Retrieve a user
POST     | [BASE]/users             | Create a new user
PUT      | [BASE]/users/[userid]    | Update an existing user
DELETE   | [BASE]/users/[userid]    | Delete a user

A `user` has the following fields:

* `name`: string
* `email`: string
* `groups`: list of integers (valid groupids)

and
* `id`: integer, assigned automatically (don't provide when creating)

### `groups` resource

 Method  | URI                      | Action
---------|--------------------------|-----------------------
GET      | [BASE]/groups            | Retrieve list of groups
GET      | [BASE]/groups/[groupid]  | Retrieve a group
POST     | [BASE]/groups            | Create a new group
PUT      | [BASE]/groups/[groupid]  | Update an existing group
DELETE   | [BASE]/groups/[groupid]  | Delete a group

A `group` has the following fields:

* `name`: string
* `users`: list of integers (valid userids)

and
* `id`: integer, assigned automatically (don't provide when creating)


## Examples

See `test_grouper.test_add_delete_update_user` and
`test_grouper.test_add_delete_update_group` for examples of using the API
with the python `requests` package.


## Design and Implementation

Some major software components this service uses are:

* the Flask web framework for routing,
* a database for storing the user and group data (currently SQLite),
* the Flask-SQLAlchemy ORM,
* the Marshmallow package for deserializing, serializing, and validating data.

I've tried to do quite a bit of validation of POST and PUT json data but I'm
sure even more could be done.

Please let me know if you have any questions, or if you would like anything
added or tweaked.  Thanks!
