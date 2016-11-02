# Grouper

Grouper is a Python web service with a JSON/REST API that manages users and
groups.

## Users

A User should have a name and unique email associated with it and can belong to
0 or more groups. 

## Groups

A group should be identified by a unique group name, and can have 0 or more
members.  


## REST API

Base URI:  http://[hostname]/grouper/api/v1.0

### `users` resource

 Method  | URI                      | Action
---------|--------------------------|-----------------------
GET      | [BASE]/users             | Retrieve list of users
GET      | [BASE]/users/[username]  | Retrieve a user
POST     | [BASE]/users             | Create a new user
PUT      | [BASE]/users/[username]  | Update an existing user
DELETE   | [BASE]/users/[username]  | Delete a user

A `user` has the following fields:

* `username`: string type
* `email`: string type
* `groups`: list of string type

### `groups` resource

 Method  | URI                      | Action
---------|--------------------------|-----------------------
GET      | [BASE]/groups             | Retrieve list of groups
GET      | [BASE]/groups/[groupname] | Retrieve a group
POST     | [BASE]/groups             | Create a new group
PUT      | [BASE]/groups/[groupname] | Update an existing group
DELETE   | [BASE]/groups/[groupname] | Delete a group


A `user` has the following fields:

* `groupname`: string type
* `users`: list of string type
