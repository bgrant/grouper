# Grouper

Grouper is a Flask-based web service with a JSON/REST API that manages users
and groups (built for my education, not for production).


## Dependencies

Check out `requirements.txt` to find the current list of dependencies.  These
dependencies can be install with `pip`, if you don't have them already.

    $ pip install -r requirements.txt


## Quickstart

If you have the dependencies installed, you can run the service with

    $ python grouper.py runserver

which will start a development server at `localhost:5000`.

You can then use the JSON/REST API from a client of your choice, for example:

    $ curl -i http://localhost:5000/grouper/api/v1/users
    $ curl -i http://localhost:5000/grouper/api/v1/groups

You can also run a set of system tests by running `pytest` in this directory
after starting the server.


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

Note: any groups listed in `groups` must already exist when creating a user.

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

Note: any users listed in `users` must already exist when creating a group.


## Examples

See `test_grouper.test_add_delete_update_user` and
`test_grouper.test_add_delete_update_group` for examples of using the API
with the python `requests` package.


## Design and Implementation

Some major software components this service uses are:

* the Flask web framework,
* a database for storing the user and group data (currently SQLite),
* the Flask-SQLAlchemy ORM,
* the Marshmallow package for deserializing, serializing, and validating data.


### Future Work

Currently, the groups a user is in (`user['groups']`) and the users a group has
(`group['users']`) are represented as lists of integer user or group ids.
These would be more readable as usernames and groupnames, but I suspect they
should really be URIs.

For updating users and groups, I currently use the PUT method and allow clients
to overwrite certain fields of a user or group.  This functionality might be
better implemented as PATCH.

I do quite a bit of validation of POST and PUT JSON data, but I'm sure even
more could be done.

Finally, the code could probably use some refactoring.  The Flask view
functions for the user and group resources are completely separate in the
codebase, but they are similar enough that they should probably be combined.
There is a lot of duplication there.  Also, if I were to continue work on the
service, I should consider splitting the code into more Python modules.

Please let me know if you have any questions, or if you would like anything
added or tweaked.  Thanks!
