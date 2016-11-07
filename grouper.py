from flask import Flask, jsonify, abort, make_response, request


app = Flask(__name__)

BASE_URI = '/grouper/api/v1'


# Initial Data


users = {
    'alice':
        {'username': 'alice',
         'email': 'alice@q.bio',
         'groups': ['wheel', 'developers'],
         },
    'bob':
        {'username': 'bob',
         'email': 'bob@q.bio',
         'groups': ['developers'],
         },
    'charlie':
        {'username': 'charlie',
         'email': 'charlie@q.bio',
         'groups': ['marketing'],
         },
    }

groups = {
    'wheel':
        {'groupname': 'wheel',
         'users': ['alice'],
         },
    'developers':
        {'groupname': 'developers',
         'users': ['alice', 'bob'],
         },
    'marketing':
        {'groupname': 'marketing',
         'users': ['charlie'],
         },
    'www':
        {'groupname': 'www',
         'users': [],
         },
    }


# Utilities


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# Users Resource


@app.route('/'.join((BASE_URI, 'users')),
           methods=['GET'])
def get_users():
    return jsonify({'users': list(users.values())})


@app.route('/'.join((BASE_URI, 'users', '<username>')),
           methods=['GET'])
def get_user(username):
    try:
        return jsonify({'user': users[username]})
    except KeyError:
        abort(404)


@app.route('/'.join((BASE_URI, 'users')),
           methods=['POST'])
def create_user():
    if not request.json:
        abort(400)
    user = dict()

    user['username'] = request.json.get('username')
    user['email'] = request.json.get('email')
    user['groups'] = []

    if not all((user['username'], user['email'])):
        abort(400)

    users['username'] = user
    return jsonify({'user': user}), 201


@app.route('/'.join((BASE_URI, 'users', '<username>')),
           methods=['DELETE'])
def delete_user(username):
    if username not in users:
        abort(404)
    del users[username]
    return jsonify({'result': True})


@app.route('/'.join((BASE_URI, 'users', '<username>')),
           methods=['PUT'])
def update_user(username):
    if username not in users:
        abort(404)
    if not request.json:
        abort(400)

    users[username]['email'] = request.json['email']

    return jsonify({'user': users[username]})


# Groups Resource


@app.route('/'.join((BASE_URI, 'groups')),
           methods=['GET'])
def get_groups():
    return jsonify({'groups': list(groups.values())})


@app.route('/'.join((BASE_URI, 'groups', '<groupname>')),
           methods=['GET'])
def get_group(groupname):
    try:
        return jsonify({'group': groups[groupname]})
    except KeyError:
        abort(404)


@app.route('/'.join((BASE_URI, 'groups')),
           methods=['POST'])
def create_group():
    if not request.json:
        abort(400)
    group = dict()

    group['groupname'] = request.json.get('groupname')
    group['users'] = request.json.get('users')

    if not group['groupname']:
        abort(400)

    groups['groupname'] = group
    return jsonify({'group': group}), 201


@app.route('/'.join((BASE_URI, 'groups', '<groupname>')),
           methods=['DELETE'])
def delete_group(groupname):
    if groupname not in groups:
        abort(404)
    del groups[groupname]
    return jsonify({'result': True})


@app.route('/'.join((BASE_URI, 'groups', '<groupname>')),
           methods=['PUT'])
def update_group(groupname):
    if groupname not in groups:
        abort(404)
    if not request.json:
        abort(400)

    groups[groupname]['users'] = request.json['users']

    return jsonify({'result': True})


if __name__ == '__main__':
    app.run(debug=True)
