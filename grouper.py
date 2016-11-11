from flask import Flask, abort, request
from flask_restful import Api, Resource
from flask_script import Manager


API_URL = '/grouper/api/v1'


app = Flask(__name__)
manager = Manager(app)
api = Api(app)


# Initial Data

users = {}
groups = {}


# Users Resource


class UserListAPI(Resource):

    def get(self):
        return {'users': list(users.values())}

    def post(self):
        if not request.json:
            abort(400)
        user = dict()

        user['username'] = request.json.get('username')
        user['email'] = request.json.get('email')
        user['groups'] = []

        if not all((user['username'], user['email'])):
            abort(400)

        users[user['username']] = user
        return {'user': user}, 201


api.add_resource(UserListAPI,
                 '/'.join((API_URL, 'users')),
                 endpoint='users')


class UserAPI(Resource):

    def get(self, username):
        try:
            return {'user': users[username]}
        except KeyError:
            abort(404)

    def put(self, username):
        if username not in users:
            abort(404)
        if not request.json:
            abort(400)

        users[username]['email'] = request.json['email']

        return {'user': users[username]}

    def delete(self, username):
        if username not in users:
            abort(404)
        del users[username]
        return {'result': True}


api.add_resource(UserAPI,
                 '/'.join((API_URL, 'users', '<string:username>')),
                 endpoint='username')


# Groups Resource


class GroupListAPI(Resource):

    def get(self):
        return {'groups': list(groups.values())}

    def post(self):
        if not request.json:
            abort(400)
        group = dict()

        group['groupname'] = request.json.get('groupname')
        group['users'] = request.json.get('users')

        if not group['groupname']:
            abort(400)

        groups[group['groupname']] = group
        return {'group': group}, 201


api.add_resource(GroupListAPI,
                 '/'.join((API_URL, 'groups')),
                 endpoint='groups')


class GroupAPI(Resource):

    def get(self, groupname):
        try:
            return {'group': groups[groupname]}
        except KeyError:
            abort(404)

    def delete(self, groupname):
        if groupname not in groups:
            abort(404)
        del groups[groupname]
        return {'result': True}

    def put(self, groupname):
        if groupname not in groups:
            abort(404)
        if not request.json:
            abort(400)

        groups[groupname]['users'] = request.json['users']

        return {'result': True}


api.add_resource(GroupAPI,
                '/'.join((API_URL, 'groups', '<string:groupname>')),
                 endpoint='groupname')


if __name__ == '__main__':
    manager.run()
