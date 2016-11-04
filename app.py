from flask import Flask, jsonify, abort


app = Flask(__name__)

BASE_URI = '/grouper/api/v1.0'


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


if __name__ == '__main__':
    app.run(debug=True)
